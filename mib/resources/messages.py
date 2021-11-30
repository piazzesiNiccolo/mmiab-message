from flask import request, jsonify
from datetime import datetime
from mib import db
from mib.dao.message_manager import MessageManager


#TODO add notification
def read_message(id_mess,id_usr):
        '''
        Return the message to read if exists
        '''
        message_to_read = MessageManager.id_message_exists(id_mess)

        if (message_to_read == None):
            response_object = {
                'status': "failed",
                "message":"Message not found"
            }
            return jsonify(response_object),404

        #TODO check in user_can_read controls about recipients
        if (MessageManager.user_can_read(id_usr,message_to_read) == False):
            response_object = {
                'status': "failed",
                "message":"User not allow to read the message"
            }
            return jsonify(response_object),401

        else:
            response_object = {
                'status': 'success',
                'message': message_to_read.serialize(),
            }

            return jsonify(response_object), 200

def message_list_sent(id_usr: int):
      
    list_of_messages = MessageManager.get_sended_message_by_id_user(id_usr)

    if (list_of_messages.length() == 0):
        response_object = {
                'status': 'failed',
                'message': 'empty list',
            }

        return jsonify(response_object), 401
    else:
        response_object = {
                'status': 'success',
                'messages': [m.serialize() for m in list_of_messages],
            }

        return jsonify(response_object), 200