from mib import db
from mib.models.message import Message
from mib.models.recipient import Recipient

from typing import List
import requests


class RecipientManager:

    @classmethod
    def retrieve_recipient_by_id(cls, message: Message, id_recipient: int) -> Recipient:
        return next(
            rcp for rcp in message.recipients if rcp.id_recipient == id_recipient,
            None
        )

    @classmethod
    def get_recipients(cls, message: Message) -> List[int]:
        if message is None:
            return []

        return [ recipient.id_recipient for recipient in message.recipients ]

    @classmethod
    def is_recipient(cls, message: Message, id: int) -> bool:
        return id in cls.get_recipients(message)

    @classmethod
    def has_opened(cls, message: Message, id: int) -> bool:
        """
        Returns true if the specified recipient has opened the given message
        """
        if message is not None:
            rcp = next(filter(lambda r: r.id_recipient == id, message.recipients))
            if rcp is not None:
                flag = rcp.has_opened
                rcp.has_opened = True
                db.session.commit()
                return flag

        return False

    @classmethod
    def recipient_can_delete(cls, message: Message, id_recipient: int) -> bool:
        return (
            message.is_arrived == True and
            cls.is_recipient(message, id_recipient)
        )

    @classmethod
    def delete_read_message(cls, message: Message, id_recipient: int) -> bool:
        rcp = cls.retrieve_recipient_by_id(message, id_recipient)
        if rcp is not None:
            if rcp.has_opened == True:
                rcp.read_deleted = True
                db.session.commit()
                return True

        return False

    @classmethod
    def set_recipients(
        cls, 
        message: Message, 
        recipients: List[int], 
        replying: bool = False
    ) -> None:
        _recipients = []
        for rcp in recipients:
            if rcp not in _recipients:
                _recipients.append(rcp)

        if replying:
            rep_msg = (
                db.session.query(Message)
                .filter(Message.id_message == message.reply_to)
                .first()
            )
            if rep_msg and rep_msg.id_sender not in _recipients:
                _recipients.insert(0, rep_msg.id_sender)

        message.recipients = [
            Recipient(id_recipient=user_id) for user_id in _recipients
        ]
        db.session.commit()

    @classmethod
    def retrieve_recipients_info(cls, id_sender: int, id_list: List[int] = None, deep_list: List[List[int]] = None) -> dict:

        if deep_list is not None:
            # The following single line of code is equal to:
            #
            #     _multi_list = []
            #     for rcp_list in deep_list:
            #         for _id in rcp_list:
            #             _multi_list.append(_id)
            #
            # but much faster.
            _multi_list = [_id for rcp_list in deep_list for _id in rcp_list]
            id_list = list(set(_multi_list))

        if id_list is None or len(id_list) == 0:
            return {}

        endpoint = f"{cls.users_endpoint()}/recipients/{id_sender}?ids={id_list}"
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



