from datetime import datetime
from datetime import timedelta
import requests
import calendar
from datetime import timedelta
from typing import List
from mib import db
from mib.dao.manager import Manager
from mib.models.message import Message
from mib.models.recipient import Recipient
from mib.events.publishers import EventPublishers
from mib.dao.recipient_manager import RecipientManager
from mib.dao.utils import Utils
from sqlalchemy import and_
from sqlalchemy.orm import Query

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
        print('ms dao', db.session.query(Message).all())
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
    def get_user_lottery_points(cls, user_id: int) -> int:
        user_info = cls.retrieve_users_info(id_list=[user_id])
        info = user_info.get(user_id, None)
        if info is not None:
            return info.get('lottery_points', 0)
        return 0

    @classmethod
    def filter_query_daily(cls, query: Query, day_dt: datetime) -> Query:
        if day_dt is not None:
            start_of_day = datetime(day_dt.year, day_dt.month, day_dt.day)
            start_of_next_day = start_of_day + timedelta(days=1)
            query = query.filter(
                Message.delivery_date >= start_of_day,
                Message.delivery_date < start_of_next_day,
            )
        return query

    @classmethod
    def filter_query_monthly(cls, query: Query, month_dt: datetime) -> Query:
        if month_dt is not None:
            month_fst = datetime(month_dt.year, month_dt.month, 1)
            next_month_fst = month_fst + timedelta(days=calendar.monthrange(month_dt.year, month_dt.month)[1])
            query = query.filter(
                Message.delivery_date >= month_fst,
                Message.delivery_date < next_month_fst,
            )
        return query


    @classmethod
    def get_sent_messages(cls, id: int, day_dt: datetime = None, month_dt: datetime = None):
        """
        Returns the list of sent messages by a specific user.
        """
        query = (
            db.session.query(Message)
            .filter(Message.id_sender == id, Message.is_sent == True)
        )
        if day_dt is not None:
            query = cls.filter_query_daily(query, day_dt)
        elif month_dt is not None:
            query = cls.filter_query_monthly(query, month_dt)

        return query.all()

    @classmethod
    def get_user_content_filter(cls,id_usr):
        try:
            url = "%s/user/filter_value/%s" % (cls.users_endpoint(),str(id_usr))
            response = requests.get(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            obj = response.json().get('toggle', False)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, False

        return code,obj

    @classmethod
    def get_received_messages(cls, id: int, day_dt: datetime = None, month_dt: datetime = None):
        """
        Returns the list of received messages by a specific user.
        """
        query = (
            db.session.query(Message)
            .filter(
                Message.is_sent == True,
                Message.is_arrived == True,
            ).filter(
                Message.recipients.any(
                    and_(Recipient.id_recipient == id, Recipient.read_deleted == False)
                )
            )
        )
        _, toggle = MessageManager.get_user_content_filter(id)
        if ( toggle == True):
            query = query.filter(Message.to_filter == False)
        
        if day_dt is not None:
            query = cls.filter_query_daily(query, day_dt=day_dt)
        elif month_dt is not None:
            query = cls.filter_query_monthly(query, month_dt=month_dt)

        #TODO check it
        # Contains for each message a flag indicating id the specified user has already opened it
        opened_dict = {
            m.id_message: next(
                (
                    rcp.has_opened
                    for rcp in m.recipients
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
            Utils.delete_message_image(message)
            return True

        return False

    @classmethod
    def send_message(cls, message: Message):
        message.is_sent = True
        db.session.commit()

    @classmethod
    def withdraw_message(cls, message: Message):
        message.is_sent = False
        EventPublishers.publish_withdraw_points({"users":[
            {"id":message.id_sender,"points":-1}
        ]})
        db.session.commit()

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

        id_list_str = ','.join([str(id) for id in id_list])
        endpoint = f"{cls.users_endpoint()}/users/display_info?ids={id_list_str}"
        try:
            response = requests.get(endpoint, timeout=cls.requests_timeout_seconds())
            if response.status_code == 200:
                recipients = response.json()['users']
                formatted_rcp = {}
                for rcp in recipients:
                    _id = rcp['id']
                    del rcp['id']
                    formatted_rcp[_id] = rcp
                return formatted_rcp
            else:
                return {}

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return {}

    @classmethod
    def get_new_arrived_messages(cls):
        messages = db.session.query(Message).filter(
            Message.is_sent == True,
            Message.is_arrived == False,
            Message.delivery_date is not None,
        )
        print(db.session.query(Message).all())

        messages_arrived = []
        for m in messages.all():
            if (m.delivery_date - datetime.now()).total_seconds() <= 0:

                m.is_arrived = True
                messages_arrived.append(m)

        db.session.commit()

        return [
            {
                "id": m.id_message,
                "date": m.delivery_date.strftime("%H:%M %d/%m/%Y"),
                "sent": m.is_sent,
                "received": m.is_arrived,
                "recipients": [recipient.id_recipient for recipient in m.recipients],
            }
            for m in messages_arrived
        ]


