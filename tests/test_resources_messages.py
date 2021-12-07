import pytest
import mock
from datetime import datetime
from mib import db
from mib.models.message import Message
from mib.models.recipient import Recipient

class TestMessages:

    @pytest.mark.parametrize('data,code', [
        ({
            'message_body': 'test body',
        }, 400),
        ({
            'id_sender': 1,
        }, 400),
        ({
            'id_sender': 1,
            'message_body': 'test body',
        }, 201),
        ({
            'id_sender': 1,
            'message_body': 'test body',
            'recipients': [2,3],
        }, 201),
        ({
            'id_sender': 1,
            'message_body': 'test body',
            'delivery_date': '10:30 10/10/2022',
        }, 201),
        ({
            'id_sender': 1,
            'message_body': 'test body',
            'delivery_date': '10:30 10/10/2022',
            'recipients': [2,3],
        }, 201),
        ({
            'id_sender': 1,
            'message_body': 'test body',
            'delivery_date': '10:30 10/10/2022',
            'recipients': [2,3],
            'image': {
                'name': 'test.png',
                'data': 'test data',
            },
        }, 201),
    ])
    def test_draft(self, test_client, data, code):
        if 'image' in data:
            with mock.patch('mib.dao.utils.Utils.save_message_image') as m:
                m.return_value = data['image']['name']
                response = test_client.post('/draft', json=data)
        else:
            response = test_client.post('/draft', json=data)
        assert response.status_code == code
        if code == 201:
            msg = db.session.query(Message).filter(Message.id_message == 1).first()
            assert msg.id_sender == data.get('id_sender', None)
            assert msg.message_body == data.get('message_body', None)
            try:
                dt = datetime.strptime(data.get('delivery_date'), '%H:%M %d/%m/%Y')
                assert msg.delivery_date == dt
            except (ValueError, TypeError):
                assert msg.delivery_date == None
            assert [r.id_recipient for r in msg.recipients] == data.get('recipients', [])
            if 'image' in data:
                assert msg.img_path == data.get('image').get('name')
            msg.recipients = []
            db.session.delete(msg)
            db.session.commit()

    @pytest.mark.parametrize('data,code', [
        ({
            'message_body': 'test update body',
        }, 400),
        ({
            'id_sender': 1,
        }, 400),
        ({
            'id_sender': 1,
            'message_body': 'test update body',
        }, 201),
        ({
            'id_sender': 1,
            'message_body': 'test update body',
            'recipients': [2,3],
        }, 201),
        ({
            'id_sender': 1,
            'message_body': 'test update body',
            'delivery_date': '20:30 10/10/2022',
        }, 201),
        ({
            'id_sender': 1,
            'message_body': 'test update body',
            'delivery_date': '20:30 10/10/2022',
            'recipients': [2,3],
        }, 201),
        ({
            'id_sender': 1,
            'message_body': 'test update body',
            'delivery_date': '20:30 10/10/2022',
            'recipients': [2,3],
            'image': {
                'name': 'test.png',
                'data': 'test data',
            },
        }, 201),
    ])
    def test_update_draft(self, test_client, draft_list, data, code):
        if 'image' in data:
            with mock.patch('mib.dao.utils.Utils.save_message_image') as m:
                m.return_value = data['image']['name']
                response = test_client.put('/draft/1/1', json=data)
        else:
            response = test_client.put('/draft/1/1', json=data)
        assert response.status_code == code
        if code == 201:
            msg = db.session.query(Message).filter(Message.id_message == 1).first()
            assert msg.id_sender == data.get('id_sender', None)
            assert msg.message_body == data.get('message_body', None)
            try:
                dt = datetime.strptime(data.get('delivery_date'), '%H:%M %d/%m/%Y')
                assert msg.delivery_date == dt
            except (ValueError, TypeError):
                assert msg.delivery_date == None
            assert [r.id_recipient for r in msg.recipients] == data.get('recipients', [])
            if 'image' in data:
                assert msg.img_path == data.get('image').get('name')

    def test_update_draft_not_existing(self, test_client):
        data = {'id_sender': 1, 'message_body': 'test' }
        response = test_client.put('/draft/1/1', json=data)
        assert response.status_code == 404

    def test_update_draft_unauthorized(self, test_client, draft_list):
        data = {'id_sender': 3, 'message_body': 'test' }
        response = test_client.put('/draft/1/3', json=data)
        assert response.status_code == 403

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
            delivery_date=datetime.strptime('10:30 10/10/2022', '%H:%M %d/%m/%Y')
        ), 400),
        (Message(
            id_sender=1, 
            is_sent=False, 
            recipients=[Recipient(id_recipient=2)]
        ), 400),
        (Message(
            id_sender=1, 
            is_sent=False, 
            delivery_date=datetime.strptime('10:30 10/10/2022', '%H:%M %d/%m/%Y'), 
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
            
    @pytest.mark.parametrize("message,lp,code", [
        (None, 0, 404),
        (Message(id_sender=2), 0, 403),
        (Message(id_sender=1, is_sent=False), 0, 400),
        (Message(id_sender=1, is_sent=True, is_arrived=True), 0, 400),
        (Message(id_sender=1, is_sent=True, is_arrived=False), 0, 400),
        # TODO: test update lottery points to ms user
        (Message(id_sender=1, is_sent=True, is_arrived=False), 2, 200),
    ])
    def test_withdraw_message(self, test_client, message, lp, code):
        if message is not None:
            db.session.add(message)
            db.session.commit()
        with mock.patch('mib.dao.message_manager.MessageManager.get_user_lottery_points') as m:
            m.return_value = lp
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
        with mock.patch('mib.dao.utils.Utils.load_message_image') as ml:
            ml.return_value = ''
            response = test_client.get('/message/1/1')
            assert response.status_code == code
        if message is not None:
            db.session.delete(message)
            db.session.commit()

    def test_message_list_draft(self, test_client, draft_list):
        with mock.patch('mib.dao.message_manager.MessageManager.retrieve_users_info') as m:
            m.return_value = {2: {'test': 'test value'}, 4: {'test': 'test value'}}
            response = test_client.get('/message/list/draft/1')
            assert response.status_code == 200
            assert len(response.json['messages']) == 2
            assert len(response.json['recipients']) == 2
        
    @pytest.mark.parametrize("retval,uri,res", [
        ( {2: {'test': 'test value'}, 4: {'test': 'test value'}, 5: {'test': 'test value'}},
            '',
            3,),
        ( {2: {'test': 'test value'}, 4: {'test': 'test value'}},
            '?y=2022&m=10&d=10',
            2,),
    ])
    def test_message_list_sent(self, test_client, sent_list, retval, uri, res):
        with mock.patch('mib.dao.message_manager.MessageManager.retrieve_users_info') as m:
            m.return_value = retval
            response = test_client.get('/message/list/sent/1' + uri)
            assert response.status_code == 200
            assert len(response.json['messages']) == res
            assert len(response.json['recipients']) == res
        
    @pytest.mark.parametrize("retval,uri,res", [
        ( {2: {'test': 'test value'}, 4: {'test': 'test value'}, 5: {'test': 'test value'}},
            '',
            3,),
        ( {2: {'test': 'test value'}, 4: {'test': 'test value'}},
            '?y=2022&m=10&d=10',
            2,),
    ])
    def test_message_list_received(self, test_client, received_list, retval, uri, res):
        with mock.patch('mib.dao.message_manager.MessageManager.retrieve_users_info') as m:
            m.return_value = retval
            response = test_client.get('/message/list/received/1' + uri)
            assert response.status_code == 200
            assert len(response.json['messages']) == res
            assert len(response.json['senders']) == res


    @pytest.mark.parametrize("uri,year,month,sent_res,rcv_res", [
        ('?y=2022&m=10', 2022, 10, 2, 3),
        ('', datetime.today().year, datetime.today().month, 0, 0),
        ('?y=2022&m=15', datetime.today().year, datetime.today().month, 0, 0),
    ])
    def test_message_list_monthly(self, test_client, received_list, sent_list, uri, year, month, sent_res, rcv_res):
        response = test_client.get('/timeline/list/1' + uri)
        assert response.status_code == 200
        _json = response.json
        _json['year'] == year
        _json['month'] == month
        assert sum(_json['sent']) == sent_res
        assert sum(_json['received']) == rcv_res

