import pytest
from datetime import datetime
from mib import create_app
from mib import db
from mib.models.message import Message
from mib.models.recipient import Recipient

@pytest.fixture(scope="session", autouse=True)
def test_client():
    app = create_app()
    with app.app_context():
        with app.test_client() as client:
            yield client

@pytest.fixture(scope='function')
def messages():
    message1 = Message(
        id_sender=1,
        message_body='test body',
        delivery_date=datetime.strptime('10/10/2022 10:30', '%d/%m/%Y %H:%M'),
        recipients=[Recipient(id_recipient=2)],
        reply_to=1,
        to_filter=True,
    )
    message2 = Message(
        id_sender=1,
        message_body='test body 2',
        delivery_date=datetime.strptime('10/10/2022 10:30', '%d/%m/%Y %H:%M'),
        recipients=[Recipient(id_recipient=4)],
        to_filter=True,
    )
    db.session.add(message1)
    db.session.add(message2)
    db.session.commit()
    yield message1, message2
    db.session.delete(message1)
    db.session.delete(message2)
    db.session.commit()


