from flask import request, jsonify
from datetime import datetime
from mib import db
from mib.dao.message_manager import MessageManager
from mib.dao.recipient_manager import RecipientManager
from mib.dao.utils import Utils
from mib.dao.content_filter import ContentFilter
from mib.models.message import Message

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
    RecipientManager.set_recipients(message, post_data.get('recipients', []))
    message.set_reply_to(post_data.get('reply_to', None))
    file_name = Utils.save_message_image(post_data.get('image', None))
    message.set_img_path(file_name)
    message.set_to_filter(ContentFilter.filter_content(post_data.get('message_body')))
    MessageManager.create_message(message)

    response_object = {
        'status': 'success',
        'message': 'Draft successfully created',
        'id_message': message.id_message,
    }
    return jsonify(response_object), 201

def update_draft(id_message, id_sender):

    message = MessageManager.retrieve_by_id(id_message)
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
    RecipientManager.set_recipients(message, post_data.get('recipients', []))
    file_name = Utils.save_message_image(post_data.get('image', None))
    message.set_img_path(file_name)
    message.set_to_filter(ContentFilter.filter_content(post_data.get('message_body')))
    MessageManager.update_message(message)

    response_object = {
        'status': 'success',
        'message': 'Draft successfully created',
    }
    return jsonify(response_object), 201

def delete_read_message(id_message, id_user):
    msg = MessageManager.retrieve_by_id(id_message)
    analysis = [
        (lambda: msg is None                                           , 'Message not found'                     , 404),
        (lambda: not RecipientManager.can_delete_read(msg, id_user)    , 'User not allowed to delete the message', 403),
        (lambda: not RecipientManager.delete_read_message(msg, id_user), 'You cannot delete an unread message'   , 400),
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
    msg = MessageManager.retrieve_by_id(id_message)
    analysis = [
        (lambda: msg is None                         , 'Message not found'                      , 404),
        (lambda: msg.id_sender != id_sender          , 'User not allowed to send the message'   , 403),
        (lambda: not MessageManager.delete_draft(msg), 'You cannot delete a sent message'       , 400),
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
    msg = MessageManager.retrieve_by_id(id_message)
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

    MessageManager.send_message(msg)
    response_object = {
        'status': 'success',
        'message': 'Message succesfully sent',
    }
    return jsonify(response_object), 200

def withdraw_message(id_message, id_user):
    msg = MessageManager.retrieve_by_id(id_message)
    analysis = [
        (lambda: msg is None             , 'Message not found'                              , 404),
        (lambda: msg.id_sender != id_user, 'User not allowed to withdraw the message'       , 403),
        (lambda: msg.is_sent == False    , 'You cannot withdraw a draft'                    , 400),
        (lambda: msg.is_arrived == True  , 'You cannot withdraw a delivered message'        , 400),
        # TODO: check lottery points
        (lambda: False                   , "You don't have enough lottery points"           , 400),
        # TODO; send to ms user request to decrease lottery points
        (lambda: False                   , 'An error occurred while withdrawing the message', 500),
    ]
    for fail, message, code in analysis:
        if fail():
            response_object = {
                'status': 'failed',
                'message': message,
            }
            return jsonify(response_object), code

    MessageManager.withdraw_message(msg)
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
    message = MessageManager.retrieve_by_id(id_message)

    if (message == None):
        response_object = {
            'status': "failed",
            "message":"Message not found"
        }
        return jsonify(response_object),404

    if (MessageManager.user_can_read(id_user,message) == False):
        response_object = {
            'status': "failed",
            "message":"User not allowed to read the message"
        }
        return jsonify(response_object),401

    else:
        message_dict = message.serialize()
        users_info = MessageManager.retrieve_users_info(
            id_list=RecipientManager.get_recipients(message) + [message.id_sender]
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

    list_of_messages = MessageManager.get_drafted_messages(id_usr)
    messages_dicts = [m.serialize() for m in list_of_messages]
    recipients_info = MessageManager.retrieve_users_info(
        #id_list=[m.id_sender for m in list_of_messages],
        deep_list=[RecipientManager.get_recipients(m) for m in list_of_messages],
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
    list_of_messages = MessageManager.get_messages_timeline_year_sent(id_usr, year, month, day )
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
        today_dt = datetime(y_i, m_i, d_i)
    except (ValueError, TypeError) as e:
        today_dt = None
      
    list_of_messages = MessageManager.get_sent_messages(id_usr, today_dt=today_dt)

    messages_dicts = [m.serialize() for m in list_of_messages]
    recipients_info = MessageManager.retrieve_users_info(
        #id_list=[m.id_sender for m in list_of_messages],
        deep_list=[RecipientManager.get_recipients(m) for m in list_of_messages],
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
        today_dt = datetime(year, month, day)
    except (ValueError, TypeError):
        today_dt = None
    
    #check open dicts
    list_of_messages, open_dict = MessageManager.get_received_messages(id_usr, today_dt)

    messages_dicts = [m.serialize() for m in list_of_messages]
    recipients_info = MessageManager.retrieve_users_info(
        id_list=[m.id_sender for m in list_of_messages],
        #deep_list=[RecipientManager.get_recipients(m) for m in list_of_messages],
    )
    response_object = {
        'status': 'success',
        'messages': messages_dicts,
        'has_opened': open_dict,
        'senders': recipients_info,
    }

    return jsonify(response_object), 200
