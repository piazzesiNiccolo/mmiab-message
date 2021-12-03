import datetime
import requests
from typing import List
from mib import db
from mib.dao.manager import Manager
from mib.models.message import Message
from mib.dao.recipient_manager import RecipientManager
from sqlalchemy import and_
import abort

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
    def get_sent_messages(id, today_dt):
        """
        Returns the list of sent messages by a specific user.
        """
        query = (
            db.session.query(Message)
            .filter(Message.id_sender == id, Message.is_sent == True)
        )
        if today_dt is not None:
            start_of_today = datetime(today_dt.year, today_dt.month, today_dt.day)
            start_of_tomorrow = start_of_today + datetime.timedelta(days=1)
            query.filter(
                Message.id_sender == id,
                Message.is_sent == True,
                Message.date_of_send >= start_of_today,
                Message.date_of_send < start_of_tomorrow,
            )
        return query.all()

    @classmethod
    def get_user_content_filter(cls,id_usr):
        try:
            url = "%s/user/filter_value/%s" % (cls.users_endpoint(),str(id_usr))
            response = requests.get(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            obj = response.json()['toggle']
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return code,obj

    @classmethod
    def get_received_messages(id, today_dt):
        """
        Returns the list of received messages by a specific user.
        """
        #received normale
        query = (
            db.session.query(Message)
            .filter(Message.is_arrived == True)
            .filter(
                Message.recipients.any(
                    and_(RecipientManager.id_recipient == id, RecipientManager.read_deleted == False)
                )
            )
        )
        code, toggle = MessageManager.get_user_content_filter(id)
        if ( toggle == True):
            query = query.filter(Message.to_filter == False)

        query = query.join(Message.id_sender == id).all()
        #fine received normale
        #timeline
        if today_dt is not None:
            start_of_today = datetime(today_dt.year, today_dt.month, today_dt.day)
            start_of_tomorrow = start_of_today + datetime.timedelta(days=1)
            query.filter(
                Message.is_sent == True,
                Message.is_arrived == True,
                Message.date_of_send >= start_of_today,
                Message.date_of_send < start_of_tomorrow,
            )

        #TODO check it
        # Contains for each message a flag indicating id the specified user has already opened it
        opened_dict = {
            m.Message.id_message: next(
                (
                    rcp.has_opened
                    for rcp in m.Message.recipients
                    if rcp.id_recipient == id
                ),
                True,
            )
            for m in query
        }

        return query.all(), opened_dict


    def delete_draft(message: Message) -> bool:
        if message.is_arrived == False and message.is_sent == False:
            message.recipients = []
            db.session.delete(message)
            db.session.commit()
            return True

        return False

    @classmethod
    def send_message(message: Message):
        message.is_sent = True
        db.session.commit()

    @classmethod
    def withdraw_message(message: Message, id_sender: int) -> bool:
        # TODO; send to ms user request to decrease lottery points
        message.is_sent = False
        db.session.commit()
        return True

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


