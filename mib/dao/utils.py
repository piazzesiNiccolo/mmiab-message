import os
import base64
from uuid import uuid4
from mib.models.message import Message
from werkzeug.utils import secure_filename
from flask import current_app

class Utils:

    @staticmethod
    def save_message_image(msg_img: dict) -> str:
        if msg_img is not None:
            b64_file = msg_img.get('data')
            bytes_file = base64.b64decode(b64_file.encode('utf-8'))
            file_name = str(uuid4()) + secure_filename(msg_img.get('name'))
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file_name)
            with open(file_path, 'wb') as file:
                file.write(bytes_file)
            return file_name
        
        return None

    @staticmethod
    def load_message_image(message: Message) -> dict:
        file_name = message.img_path
        b64_file, type = '', ''
        if file_name is not None:
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file_name)
            try:
                with open(file_path, 'rb') as file:
                    b64_file = base64.b64encode(file.read()).decode("utf8")
                    type = os.path.splitext(file_name)[1][1:]
            except FileNotFoundError:
                b64_file, type = '', ''

        return {
            'name': file_name,
            'data': b64_file,
            'type': type,
        }

    @staticmethod
    def delete_message_image(message: Message) -> dict:
        file_name = message.img_path
        if file_name is not None:
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file_name)
            try:
                os.remove(file_path)
                return True
            except FileNotFoundError:
                return False

        return False

