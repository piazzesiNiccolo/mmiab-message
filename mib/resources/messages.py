from flask import request, jsonify
from datetime import datetime
from mib import db
from mib.dao.message_manager import MessageManager



def read_message(id_mess):
        '''
        Return the message to read if exists
        '''
        message_to_read = MessageManager.id_message_exists(id_mess)

        if (message_to_read == 0):
            response_object = {
                'status': "failed",
                "message":"Message not found"
            }
            return jsonify(response_object),404
        else:
            response_object = {
                'status': 'success',
                'message': [message_to_read.serialize()],
            }

            return jsonify(response_object), 202