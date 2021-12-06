from flask import request, jsonify
from datetime import datetime
from mib.dao.message_manager import MessageManager as MM
from mib.dao.recipient_manager import RecipientManager as RM
from mib.dao.utils import Utils
from mib.dao.content_filter import ContentFilter
from mib.events.publishers import EventPublishers
from mib.models.message import Message
import calendar

def draft():
    post_data = request.get_json()

    message = Message()
    message.set_id_sender(post_data.get('id_sender'))
    message.set_message_body(post_data.get('message_body'))
    try:
        delivery_date = datetime.strptime( 
            post_data.get('delivery_date', None), 
            '%d/%m/%Y %H:%M',
        )
    except (ValueError, TypeError):
        delivery_date = None
    message.set_delivery_date(delivery_date)
    RM.set_recipients(message, post_data.get('recipients', []))
    message.set_reply_to(post_data.get('reply_to', None))
    file_name = Utils.save_message_image(post_data.get('image', None))
    message.set_img_path(file_name)
    message.set_to_filter(ContentFilter.filter_content(post_data.get('message_body')))
    MM.create_message(message)

    response_object = {
        'status': 'success',
        'message': 'Draft successfully created',
        'id_message': message.id_message,
    }
    return jsonify(response_object), 201

def update_draft(id_message, id_sender):

    message = MM.retrieve_by_id(id_message)
    if message is None:
        response_object = {
            'status': 'failed',
            'message': 'Message not found',
        }
        return jsonify(response_object), 404
    
    post_data = request.get_json()

    if id_sender != message.id_sender:
        response_object = {
            'status': 'failed',
            'message': 'User not allowed to edit the message',
        }
        return jsonify(response_object), 403

    message.set_message_body(post_data.get('message_body'))
    try:
        delivery_date = datetime.strptime( 
            post_data.get('delivery_date', None), 
            '%d/%m/%Y %H:%M',
        )
    except (ValueError, TypeError):
        delivery_date = None
    message.set_delivery_date(delivery_date)
    RM.set_recipients(message, post_data.get('recipients', []))
    file_name = Utils.save_message_image(post_data.get('image', None))
    message.set_img_path(file_name)
    message.set_to_filter(ContentFilter.filter_content(post_data.get('message_body')))
    MM.update_message(message)

    response_object = {
        'status': 'success',
        'message': 'Draft successfully created',
    }
    return jsonify(response_object), 201

def delete_read_message(id_message, id_user):
    msg = MM.retrieve_by_id(id_message)
    analysis = [
        (lambda: msg is None                             , 'Message not found'                     , 404),
        (lambda: not RM.can_delete_read(msg, id_user)    , 'User not allowed to delete the message', 403),
        (lambda: not RM.delete_read_message(msg, id_user), 'You cannot delete an unread message'   , 400),
    ]
    for fail, message, code in analysis:
        if fail():
            response_object = {
                'status': 'failed',
                'message': message,
            }
            return jsonify(response_object), code

    response_object = {
        'status': 'success',
        'message': 'Message successfully deleted',
    }
    return jsonify(response_object), 200

def delete_draft(id_message, id_sender):
    msg = MM.retrieve_by_id(id_message)
    analysis = [
        (lambda: msg is None               , 'Message not found'                      , 404),
        (lambda: msg.id_sender != id_sender, 'User not allowed to send the message'   , 403),
        (lambda: not MM.delete_draft(msg)  , 'You cannot delete a sent message'       , 400),
    ]
    for fail, message, code in analysis:
        if fail():
            response_object = {
                'status': 'failed',
                'message': message,
            }
            return jsonify(response_object), code

    response_object = {
        'status': 'success',
        'message': 'Draft successfully deleted',
    }
    return jsonify(response_object), 200

def send_message(id_message, id_user):
    msg = MM.retrieve_by_id(id_message)
    analysis = [
        (lambda: msg is None              , 'Message not found'                       , 404),
        (lambda: msg.id_sender != id_user , 'User not allowed to send the message'    , 403),
        (lambda: msg.is_sent == True      , 'Message already sent'                    , 400),
        (lambda: msg.delivery_date is None, 'You must set a delivery date first'      , 400),
        (lambda: len(msg.recipients) == 0 , 'You must pick a list of recipients first', 400),
    ]
    for fail, message, code in analysis:
        if fail():
            response_object = {
                'status': 'failed',
                'message': message,
            }
            return jsonify(response_object), code

    MM.send_message(msg)
    response_object = {
        'status': 'success',
        'message': 'Message succesfully sent',
    }
    return jsonify(response_object), 200

def withdraw_message(id_message, id_user):
    msg = MM.retrieve_by_id(id_message)
    analysis = [
        (lambda: msg is None                             , 'Message not found'                              , 404),
        (lambda: msg.id_sender != id_user                , 'User not allowed to withdraw the message'       , 403),
        (lambda: msg.is_sent == False                    , 'You cannot withdraw a draft'                    , 400),
        (lambda: msg.is_arrived == True                  , 'You cannot withdraw a delivered message'        , 400),
        # TODO: check lottery points
        (lambda: MM.get_user_lottery_points(id_user) <= 0, "You don't have enough lottery points"           , 400),
        # TODO; send to ms user request to decrease lottery points
        (lambda: False                                   , 'An error occurred while withdrawing the message', 500),
    ]
    for fail, message, code in analysis:
        if fail():
            response_object = {
                'status': 'failed',
                'message': message,
            }
            return jsonify(response_object), code

    MM.withdraw_message(msg)
    response_object = {
        'status': 'success',
        'message': 'Message succesfully withdrawn',
    }
    return jsonify(response_object), 200

# TODO: add notification
def read_message(id_message, id_user):
    '''
    Return the message to read if exists
    '''
    message = MM.retrieve_by_id(id_message)

    if (message == None):
        response_object = {
            'status': "failed",
            "message":"Message not found"
        }
        return jsonify(response_object),404

    if (MM.user_can_read(id_user,message) == False):
        response_object = {
            'status': "failed",
            "message":"User not allowed to read the message"
        }
        return jsonify(response_object),401

    else:
        if not RM.has_opened(message,id_user):
            payload = {"notifications":[{
                "id_message":message.id_message,
                "id_user":message.id_sender,
                "for_recipient":False,
                "for_sender":True,
                "for_lottery":True,
                "from_recipient":id_user
            }]}
            EventPublishers.publish_add_notify(payload)
        message_dict = message.serialize()
        users_info = MM.retrieve_users_info(
            id_list=RM.get_recipients(message) + [message.id_sender]
        )
        response_object = {
            'status': 'success',
            'message': 'Message retrieved succesfully',
            'obj': message_dict,
            'users': users_info,
            'image': Utils.load_message_image(message),
        }
        return jsonify(response_object), 200

def message_list_draft(id_usr: int):

    list_of_messages = MM.get_drafted_messages(id_usr)
    messages_dicts = [m.serialize() for m in list_of_messages]
    recipients_info = MM.retrieve_users_info(
        #id_list=[m.id_sender for m in list_of_messages],
        deep_list=[RM.get_recipients(m) for m in list_of_messages],
    )
    response_object = {
        'status': 'success',
        'messages': messages_dicts,
        'recipients': recipients_info,
    }

    return jsonify(response_object), 200

'''
def message_timeline_daily_sent(id_usr: int, data: datetime ):

    year, month, day = data.year, data.month, data.day
    list_of_messages = MM.get_messages_timeline_year_sent(id_usr, year, month, day )
    messages_dicts = [m.serialize() for m in list_of_messages]

    response_object = {
        'status': 'success',
        'messages': messages_dicts,
    }

    return jsonify(response_object), 200
'''

def message_list_sent(id_usr: int):

    year = request.args.get('y',None)
    month = request.args.get('m',None)
    day = request.args.get('d',None)

    try:
        y_i, m_i, d_i = int(year), int(month), int(day)
        day_dt = datetime(y_i, m_i, d_i)
    except (ValueError, TypeError) as e:
        day_dt = None
      
    list_of_messages = MM.get_sent_messages(id_usr, day_dt=day_dt)

    messages_dicts = [m.serialize() for m in list_of_messages]
    recipients_info = MM.retrieve_users_info(
        #id_list=[m.id_sender for m in list_of_messages],
        deep_list=[RM.get_recipients(m) for m in list_of_messages],
    )
    response_object = {
        'status': 'success',
        'messages': messages_dicts,
        'recipients': recipients_info,
    }

    return jsonify(response_object), 200

def message_list_received(id_usr: int):

    year = request.args.get('y',None)
    month = request.args.get('m',None)
    day = request.args.get('d',None)

    try:
        y_i, m_i, d_i = int(year), int(month), int(day)
        day_dt = datetime(y_i, m_i, d_i)
    except (ValueError, TypeError):
        day_dt = None
    
    #check open dicts
    list_of_messages, open_dict = MM.get_received_messages(id_usr, day_dt=day_dt)

    messages_dicts = [m.serialize() for m in list_of_messages]
    recipients_info = MM.retrieve_users_info(
        id_list=[m.id_sender for m in list_of_messages],
        #deep_list=[RM.get_recipients(m) for m in list_of_messages],
    )
    response_object = {
        'status': 'success',
        'messages': messages_dicts,
        'has_opened': open_dict,
        'senders': recipients_info,
    }

    return jsonify(response_object), 200

def message_list_monthly(id_usr: int):

    year = request.args.get('y',None)
    month = request.args.get('m',None)

    try:
        y_i, m_i = int(year), int(month)
        month_dt = datetime(y_i, m_i, 1)
    except (ValueError, TypeError) as e:
        month_dt = datetime.today()
    

    list_of_messages_sent = MM.get_sent_messages(id_usr, month_dt=month_dt)

    list_of_messages_received, _ = MM.get_received_messages(id_usr,month_dt=month_dt)

    _, number_of_days = calendar.monthrange(month_dt.year, month_dt.month)
    sent, received = number_of_days * [0], number_of_days * [0]

    for elem in list_of_messages_sent:
        sent[elem.delivery_date.day - 1] += 1

    for elem in list_of_messages_received:
        received[elem.delivery_date.day - 1] += 1

    response_object = {
        'status': 'success',
        'sent': sent,
        'received': received,
        'year': month_dt.year,
        'month': month_dt.month,
    }

    return jsonify(response_object), 200
