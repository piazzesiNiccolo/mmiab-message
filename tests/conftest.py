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
        delivery_date=datetime.strptime('10:30 10/10/2022', '%H:%M %d/%m/%Y'),
        recipients=[Recipient(id_recipient=2)],
        reply_to=1,
        to_filter=True,
    )
    message2 = Message(
        id_sender=1,
        message_body='test body 2',
        delivery_date=datetime.strptime('10:30 10/10/2022', '%H:%M %d/%m/%Y'),
        recipients=[Recipient(id_recipient=4)],
        to_filter=True,
    )
    db.session.add(message1)
    db.session.add(message2)
    db.session.commit()
    yield message1, message2
    message1.recipients = []
    db.session.delete(message1)
    message2.recipients = []
    db.session.delete(message2)
    db.session.commit()

@pytest.fixture(scope='function')
def draft_list():
    message1 = Message(
        id_sender=1,
        message_body='test body',
        delivery_date=datetime.strptime('10:30 10/10/2022', '%H:%M %d/%m/%Y'),
        recipients=[Recipient(id_recipient=2)],
    )
    message2 = Message(
        id_sender=1,
        message_body='test body 2',
        delivery_date=datetime.strptime('10:30 10/10/2022', '%H:%M %d/%m/%Y'),
        recipients=[Recipient(id_recipient=4)],
    )
    db.session.add(message1)
    db.session.add(message2)
    db.session.commit()
    yield message1, message2
    message1.recipients = []
    db.session.delete(message1)
    message2.recipients = []
    db.session.delete(message2)
    db.session.commit()


@pytest.fixture(scope='function')
def sent_list():
    message1 = Message(
        id_sender=1,
        message_body='test body',
        delivery_date=datetime.strptime('10:30 10/10/2022', '%H:%M %d/%m/%Y'),
        recipients=[Recipient(id_recipient=2)],
        is_sent = True,
    )
    message2 = Message(
        id_sender=1,
        message_body='test body 2',
        delivery_date=datetime.strptime('10:30 10/10/2022', '%H:%M %d/%m/%Y'),
        recipients=[Recipient(id_recipient=4)],
        is_sent = True,
    )
    message3 = Message(
        id_sender=1,
        message_body='test body 3',
        delivery_date=datetime.strptime('10:30 09/11/2022', '%H:%M %d/%m/%Y'),
        recipients=[Recipient(id_recipient=5)],
        is_sent = True,
    )
    db.session.add(message1)
    db.session.add(message2)
    db.session.add(message3)
    db.session.commit()
    yield message1, message2, message3
    message1.recipients = []
    db.session.delete(message1)
    message2.recipients = []
    db.session.delete(message2)
    message3.recipients = []
    db.session.delete(message3)
    db.session.commit()

@pytest.fixture(scope='function')
def received_list():
    message1 = Message(
        id_sender=2,
        message_body='test body',
        delivery_date=datetime.strptime('10:30 10/10/2022', '%H:%M %d/%m/%Y'),
        recipients=[Recipient(id_recipient=1)],
        is_sent=True,
        is_arrived=True,
    )
    message2 = Message(
        id_sender=2,
        message_body='test body 2',
        delivery_date=datetime.strptime('09:30 10/10/2022', '%H:%M %d/%m/%Y'),
        recipients=[Recipient(id_recipient=4), Recipient(id_recipient=1)],
        is_sent=True,
        is_arrived=True,
    )
    message3 = Message(
        id_sender=2,
        message_body='test body 3',
        delivery_date=datetime.strptime('10:30 09/10/2022', '%H:%M %d/%m/%Y'),
        recipients=[Recipient(id_recipient=6), Recipient(id_recipient=1), Recipient(id_recipient=5)],
        to_filter=True,
        is_sent=True,
        is_arrived=True,
    )
    message4 = Message(
        id_sender=2,
        message_body='test body 3',
        delivery_date=datetime.strptime('10:30 09/10/2022', '%H:%M %d/%m/%Y'),
        recipients=[Recipient(id_recipient=3), Recipient(id_recipient=5)],
        is_sent=True,
        is_arrived=True,
    )
    message5 = Message(
        id_sender=2,
        message_body='test body 3',
        delivery_date=datetime.strptime('10:30 09/11/2022', '%H:%M %d/%m/%Y'),
        recipients=[Recipient(id_recipient=1, read_deleted=True), Recipient(id_recipient=5)],
        is_sent=True,
        is_arrived=True,
    )
    db.session.add(message1)
    db.session.add(message2)
    db.session.add(message3)
    db.session.add(message4)
    db.session.add(message5)
    db.session.commit()
    yield message1, message2, message3, message4, message5
    message1.recipients = []
    db.session.delete(message1)
    message2.recipients = []
    db.session.delete(message2)
    message3.recipients = []
    db.session.delete(message3)
    message4.recipients = []
    db.session.delete(message4)
    message5.recipients = []
    db.session.delete(message5)
    db.session.commit()

