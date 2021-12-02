import datetime
import requests
from typing import List
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
    def get_drafted_messages(cls, id):
        """
        Returns the list of drafted messages by a specific user.
        """
        mess = (
            db.session.query(Message)
            .filter(
                Message.id_sender == id,
                Message.is_sent == False,
                Message.is_arrived == False,
            )
            .all()
        )
        return mess

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

    @classmethod
    def get_messages_timeline_year_sent(id_usr: int, year: int, month: int, day: int ):
        """
        Returns a list of sent messages scheduled for a specific day.
        """
        start_of_today = datetime(year, month, day)
        start_of_tomorrow = start_of_today + datetime.timedelta(days=1)
        result = (
            db.session.query(Message)
            .filter(
                Message.id_sender == id,
                Message.is_sent == True,
                Message.date_of_send >= start_of_today,
                Message.date_of_send < start_of_tomorrow,
            )
            .all()
        )
        return result


    @classmethod
    def retrieve_users_info(cls, id_list: List[int] = [], deep_list: List[List[int]] = []) -> dict:

        # The following single line of code is equal to:
        #
        #     _multi_list = []
        #     for rcp_list in deep_list:
        #         for _id in rcp_list:
        #             _multi_list.append(_id)
        #
        # but much faster.
        _multi_list = [_id for user_list in deep_list for _id in user_list]
        id_list.extend(_multi_list)
        id_list = list(set(id_list))

        if len(id_list) == 0:
            return {}

        endpoint = f"{cls.users_endpoint()}/users/display_info/?ids={id_list}"
        try:
            response = requests.get(endpoint, timeout=cls.requests_timeout_seconds())
            if response.status_code == 200:
                recipients = response.json()['recipients']
                formatted_rcp = {}
                for rcp in recipients:
                    if rcp['id'] not in formatted_rcp:
                        _id = rcp['id']
                        del rcp['id']
                        formatted_rcp[_id] = rcp
                return formatted_rcp
            else:
                return {}

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return {}


