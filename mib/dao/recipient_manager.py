from mib import db
from mib.models.message import Message
from mib.models.recipient import Recipient

from typing import List


class RecipientManager:
    """
    Wrapper class  for all db operations involving recipients
    """

    @classmethod
    def retrieve_recipient_by_id(cls, message: Message, id_recipient: int) -> Recipient:
        if message is None:
            return None

        return next(
            (rcp for rcp in message.recipients if rcp.id_recipient == id_recipient),
            None,
        )

    @classmethod
    def get_recipients(cls, message: Message) -> List[int]:
        if message is None:
            return []

        return [recipient.id_recipient for recipient in message.recipients]

    @classmethod
    def is_recipient(cls, message: Message, id: int) -> bool:
        if message is None:
            return False

        return id in cls.get_recipients(message)

    @classmethod
    def has_opened(cls, message: Message, id: int) -> bool:
        """
        Returns true if the specified recipient has opened the given message
        """
        if message is not None:
            try:
                rcp = next(filter(lambda r: r.id_recipient == id, message.recipients))
                flag = rcp.has_opened
                rcp.has_opened = True
                db.session.commit()
                return flag
            except StopIteration:
                return True

        return True

    @classmethod
    def can_delete_read(cls, message: Message, id_recipient: int) -> bool:
        if message is None:
            return False

        return message.is_arrived == True and cls.is_recipient(message, id_recipient)

    @classmethod
    def delete_read_message(cls, message: Message, id_recipient: int) -> bool:
        if message is None:
            return False

        rcp = cls.retrieve_recipient_by_id(message, id_recipient)
        if rcp is not None:
            if rcp.has_opened == True:
                rcp.read_deleted = True
                db.session.commit()
                return True

        return False

    @classmethod
    def set_recipients(
        cls, message: Message, recipients: List[int], replying: bool = False
    ) -> None:
        # this is done this way to keep the order of recipients
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
