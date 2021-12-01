from mib import db
from mib.dao.manager import Manager
from mib.models.message import Message

from flask import current_app as app

class MessageManager(Manager):

    @classmethod
    def users_endpoint(cls):
        return app.config['USERS_MS_URL']
    
    @classmethod
    def requests_timeout_seconds(cls):
        return app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
    def create_message(cls, message: Message):
        Manager.create(message=message)
    
    @classmethod
    def update_message(cls, message: Message):
        Manager.update(message=message)

    '''
    @classmethod
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
    '''

    @classmethod
    def retrieve_by_id(cls, id_: int):
        Manager.check_none(id=id_)
        return db.session.query(Message).filter(Message.id_message == id_).first()
        

    @classmethod
    def get_sent_messages(cls, id):
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
    @classmethod
    def user_can_read(cls, user_id: int, message: Message) -> bool:
        '''
        recipients = [rcp.id_recipient for rcp in message.recipients]
        if message.is_arrived == True:
            if user_id not in recipients and user_id != message.id_sender:
                return False
        elif user_id != message.id_sender:
            return False
        '''
        recipients = [rcp.id_recipient for rcp in message.recipients]
        if message.is_arrived == True:
            if user_id not in recipients and user_id != message.id_sender:
                return False
        elif user_id != message.id_sender:
            return False

        return True
