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
            post_data.get('delivery_date'), 
            post_data.get('delivery_date_format'),
        )
    except ValueError:
        delivery_date = None
    message.set_delivery_date(delivery_date)
    RecipientManager.set_recipients(message, post_data.get('recipients'))
    message.set_reply_to(post_data.get('reply_to'))
    file_name = Utils.save_message_image(post_data.get('image'))
    message.set_img_path(file_name)
    message.set_to_filter(ContentFilter.filter_content(post_data.get('message_body')))
    MessageManager.create_message(message)

    response_object = {
        'status': 'success',
        'message': 'Draft successfully created',
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
            post_data.get('delivery_date'), 
            post_data.get('delivery_date_format'),
        )
    except ValueError:
        delivery_date = None
    message.set_delivery_date(delivery_date)
    RecipientManager.set_recipients(message, post_data.get('recipients'))
    file_name = Utils.save_message_image(post_data.get('image'))
    message.set_img_path(file_name)
    message.set_to_filter(ContentFilter.filter_content(post_data.get('message_body')))
    MessageManager.update_message(message)

    response_object = {
        'status': 'success',
        'message': 'Draft successfully created',
    }
    return jsonify(response_object), 201

# TODO: add notification
def read_message(id_mess, id_usr):
    '''
    Return the message to read if exists
    '''
    message = MessageManager.retrieve_by_id(id_mess)

    if (message == None):
        response_object = {
            'status': "failed",
            "message":"Message not found"
        }
        return jsonify(response_object),404

    if (MessageManager.user_can_read(id_usr,message) == False):
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
            'message': message_dict,
            'users': users_info,
            'image': Utils.load_message_image(message),
        }
        return jsonify(response_object), 200

def message_list_sent(id_usr: int):
      
    list_of_messages = MessageManager.get_sent_messages(id_usr)

    messages_dicts = [m.serialize() for m in list_of_messages]
    recipients_info = MessageManager.retrieve_users_info(
        id_list=[m.id_sender for m in list_of_messages],
        deep_list=[RecipientManager.get_recipients(m) for m in list_of_messages],
    )
    message_images = [Utils.load_message_image(m) for m in list_of_messages]
    response_object = {
        'status': 'success',
        'messages': messages_dicts,
        'recipients': recipients_info,
        'images': message_images,
    }

    return jsonify(response_object), 200

def message_list_received(id_usr: int):
      
    list_of_messages = MessageManager.get_received_messages(id_usr)

    messages_dicts = [m.serialize() for m in list_of_messages]
    #TODO fix info NOT recipients YES sender
    recipients_info = RecipientManager.retrieve_recipients_info(
        id_usr,
        deep_list=[m.recipients for m in list_of_messages],
    )
    #######################################################
    message_images = [Utils.load_message_image(m) for m in list_of_messages]
    response_object = {
        'status': 'success',
        'messages': messages_dicts,
        'recipients': recipients_info,
        'images': message_images,
    }

    return jsonify(response_object), 200

def message_list_received(id_usr: int):
      
    list_of_messages = MessageManager.get_received_messages(id_usr)

    messages_dicts = [m.serialize() for m in list_of_messages]
    #TODO fix info NOT recipients YES sender
    recipients_info = RecipientManager.retrieve_recipients_info(
        id_usr,
        deep_list=[m.recipients for m in list_of_messages],
    )
    #######################################################
    message_images = [Utils.load_message_image(m) for m in list_of_messages]
    response_object = {
        'status': 'success',
        'messages': messages_dicts,
        'recipients': recipients_info,
        'images': message_images,
    }

    return jsonify(response_object), 200
