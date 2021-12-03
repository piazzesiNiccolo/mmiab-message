import pytest
import mock
from datetime import datetime
from mib import db
from mib.models.message import Message
from mib.models.recipient import Recipient

class TestMessages:

    @pytest.mark.parametrize("message,code", [
        (None, 404),
        (Message(is_arrived=False), 403),
        (Message(is_arrived=True, recipients=[Recipient(id_recipient=2)]), 403),
        (Message(is_arrived=True, recipients=[Recipient(id_recipient=1, has_opened=False)]), 400),
        (Message(is_arrived=True, recipients=[Recipient(id_recipient=1, has_opened=True)]), 200),
    ])
    def test_delete_read_message(self, test_client, message, code):
        if message is not None:
            db.session.add(message)
            db.session.commit()
        response = test_client.delete('/message/1/1')
        assert response.status_code == code
        if message is not None:
            db.session.delete(message)
            db.session.commit()

    @pytest.mark.parametrize("message,code", [
        (None, 404),
        (Message(id_sender=2, is_sent=False), 403),
        (Message(id_sender=1, is_sent=True), 400),
        (Message(id_sender=1, is_arrived=True), 400),
        (Message(id_sender=1, is_sent=False), 200),
    ])
    def test_delete_draft(self, test_client, message, code):
        if message is not None:
            db.session.add(message)
            db.session.commit()
        response = test_client.delete('/draft/1/1')
        assert response.status_code == code
        if message is not None and code != 200:
            db.session.delete(message)
            db.session.commit()
            
    @pytest.mark.parametrize("message,code", [
        (None, 404),
        (Message(id_sender=2), 403),
        (Message(id_sender=1, is_sent=True), 400),
        (Message(id_sender=1, is_arrived=True), 400),
        (Message(id_sender=1, is_sent=False), 400),
        (Message(
            id_sender=1, 
            is_sent=False, 
            delivery_date=datetime.strptime('10/10/2022 10:30', '%d/%m/%Y %H:%M')
        ), 400),
        (Message(
            id_sender=1, 
            is_sent=False, 
            recipients=[Recipient(id_recipient=2)]
        ), 400),
        (Message(
            id_sender=1, 
            is_sent=False, 
            delivery_date=datetime.strptime('10/10/2022 10:30', '%d/%m/%Y %H:%M'), 
            recipients=[Recipient(id_recipient=2)]
        ), 200),
    ])
    def test_send_message(self, test_client, message, code):
        if message is not None:
            db.session.add(message)
            db.session.commit()
        response = test_client.post('/message/send/1/1')
        assert response.status_code == code
        if message is not None:
            db.session.delete(message)
            db.session.commit()
            
    @pytest.mark.parametrize("message,code", [
        (None, 404),
        (Message(id_sender=2), 403),
        (Message(id_sender=1, is_sent=False), 400),
        (Message(id_sender=1, is_sent=True, is_arrived=True), 400),
        # TODO: test check for lottery points
        # TODO: test update lottery points to ms user
        (Message(id_sender=1, is_sent=True, is_arrived=False), 200),
    ])
    def test_withdraw_message(self, test_client, message, code):
        if message is not None:
            db.session.add(message)
            db.session.commit()
        response = test_client.post('/message/withdraw/1/1')
        assert response.status_code == code
        if message is not None:
            db.session.delete(message)
            db.session.commit()
            
    @pytest.mark.parametrize("message,code", [
        (None, 404),
        (Message(id_sender=2, is_arrived=False), 401),
        (Message(id_sender=2, is_arrived=True, recipients=[Recipient(id_recipient=3)]), 401),
        (Message(id_sender=1, is_arrived=True, recipients=[Recipient(id_recipient=3)]), 200),
        (Message(id_sender=2, is_arrived=True, recipients=[Recipient(id_recipient=1)]), 200),
    ])
    def test_read_message(self, test_client, message, code):
        if message is not None:
            db.session.add(message)
            db.session.commit()
        with mock.patch('mib.models.message.Message.serialize') as m:
            with mock.patch('mib.dao.utils.Utils.load_message_image') as ml:
                ml.return_value = ''
                m.return_value = {}
                response = test_client.get('/message/1/1')
                assert response.status_code == code
        if message is not None:
            db.session.delete(message)
            db.session.commit()
            



