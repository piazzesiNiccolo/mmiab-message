from mib import db
from mib.dao.manager import Manager
from mib.models.message import Message
from typing import List

class MessageManager(Manager):

    @staticmethod
    def id_message_exists(id_message):
        """
        Checks that the id passed corresponds to a message in the db and returns it, raising an exception
        if no message is found
        """
        message = (
            db.session.query(Message).filter(Message.id_message == id_message).first()
        )

        if message is None:
            return 0 #add exception
        else:
            return message
