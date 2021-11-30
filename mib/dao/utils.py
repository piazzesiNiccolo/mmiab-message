import os
import base64
from uuid import uuid4
from werkzeug.utils import secure_filename
from flask import current_app

class Utils:

    @staticmethod
    def save_message_image(msg_img: dict) -> str:
        if msg_img != '':
            b64_file = msg_img.get('data')
            bytes_file = base64.b64decode(b64_file.encode('utf-8'))
            file_name = str(uuid4()) + secure_filename(msg_img.get('name'))
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file_name)
            with open(file_path, 'wb') as file:
                file.write(bytes_file)
            return file_name
        
        return None

