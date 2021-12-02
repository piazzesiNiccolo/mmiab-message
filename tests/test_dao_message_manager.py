import pytest
from datetime import datetime
from mib import db
from mib.models.recipient import Recipient
from mib.models.message import Message
from mib.dao.message_manager import MessageManager

class TestMessageManager:

    @pytest.mark.parametrize("dict", [
        dict(
            id_sender=1,
            message_body='test body',
            delivery_date=datetime.strptime('10/10/2022 10:30', '%d/%m/%Y %H:%M'),
            recipients=[Recipient(id_recipient=2)],
            reply_to=1,
            to_filter=True,
        ),
        dict(
            id_sender=1,
            message_body='test body',
            recipients=[Recipient(id_recipient=2)],
            to_filter=True,
        ),
        dict(
            id_sender=1,
            message_body='test body',
            delivery_date=datetime.strptime('10/10/2022 10:30', '%d/%m/%Y %H:%M'),
            to_filter=True,
        ),
        dict(
            id_sender=1,
            message_body='test body',
            delivery_date=datetime.strptime('10/10/2022 10:30', '%d/%m/%Y %H:%M'),
            recipients=[Recipient(id_recipient=2)],
            to_filter=False,
        ),
    ])
    def test_create_message_ok(self, dict):
        message = Message(**dict)
        MessageManager.create_message(message)
        assert db.session.query(Message).count() == 1
        message.recipients = []
        db.session.delete(message)
        db.session.commit()

