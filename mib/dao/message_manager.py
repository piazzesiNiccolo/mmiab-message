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
            return None
        else:
            return message

    @staticmethod
    def get_sended_message_by_id_user(id):
        """
        Returns the list of sent messages by a specific user.
        """
        mess = (
            db.session.query(Message)
            .filter(Message.id_sender == id, Message.is_sent == True)
            .all()
        )
        return mess

    #TODO add some checks about recipient
    @staticmethod
    def user_can_read(user_id: int, message: Message) -> bool:
        '''
        recipients = [rcp.id_recipient for rcp in message.recipients]
        if message.is_arrived == True:
            if user_id not in recipients and user_id != message.id_sender:
                return False
        elif user_id != message.id_sender:
            return False
        '''
        if user_id != message.id_sender:
            return False
        return True
