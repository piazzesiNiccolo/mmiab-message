import requests
import mock
import pytest
from datetime import datetime,timedelta
from mib import db
from mib.models.recipient import Recipient
from mib.models.message import Message
from mib.dao.message_manager import MessageManager
from testing.fake_response import MockResponse

class TestMessageManager:

    @pytest.mark.parametrize("dict", [
        dict(
            id_sender=1,
            message_body='test body',
            delivery_date=datetime.strptime('10/10/2022 10:30', '%H:%M %d/%m/%Y'),
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
            delivery_date=datetime.strptime('10/10/2022 10:30', '%H:%M %d/%m/%Y'),
            to_filter=True,
        ),
        dict(
            id_sender=1,
            message_body='test body',
            delivery_date=datetime.strptime('10/10/2022 10:30', '%H:%M %d/%m/%Y'),
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

    def test_update_message_ok(self, messages):
        message, _ = messages
        message.message_body='updated test body'
        message.delivery_date=datetime.strptime('11/11/2022 10:30', '%H:%M %d/%m/%Y')
        message.recipients=[Recipient(id_recipient=3)]
        message.to_filter=False
        MessageManager.update_message(message)
        q = db.session.query(Message)
        assert q.count() == 2
        assert q.first().message_body == 'updated test body'

    def test_retrieve_by_id(self, messages):
        _message = MessageManager.retrieve_by_id(1)
        assert _message.id_message == 1

    def test_get_drafted_messages(self, draft_list):
        _messages = MessageManager.get_drafted_messages(1)
        assert all(map(lambda m: m.id_sender == 1 and m.is_sent == False, _messages))
        assert len(_messages) == 2

    @pytest.mark.parametrize('retval,res', [
        ({}, 0),
        ({1: {}}, 0),
        ({1: {'lottery_points': 2}}, 2),
    ])
    def test_get_user_lottery_points(self, retval, res):
        with mock.patch('mib.dao.message_manager.MessageManager.retrieve_users_info') as m:
            m.return_value = retval
            assert MessageManager.get_user_lottery_points(1) == res

    @pytest.mark.parametrize('date,res', [
        (datetime(2022,10,10), 2),
        (None, 5),
    ])
    def test_filter_query_daily(self, received_list, date, res):
        query = db.session.query(Message)
        query = MessageManager.filter_query_daily(query, day_dt=date)
        assert query.count() == res

    @pytest.mark.parametrize('date,res', [
        (datetime(2022,10,10), 4),
        (None, 5),
    ])
    def test_filter_query_monthly(self, received_list, date, res):
        query = db.session.query(Message)
        query = MessageManager.filter_query_monthly(query, month_dt=date)
        assert query.count() == res

    @pytest.mark.parametrize('day_dt, month_dt, nres', [
        (None, None, 3,),
        (datetime(2022,10,10), None, 2),
        (None, datetime(2022,10,1), 2),
        (datetime(2022,10,10), datetime(2022,10,10), 2),
    ])
    def test_get_sent_messages(self, sent_list, day_dt, month_dt, nres):
        _messages = MessageManager.get_sent_messages(1, day_dt=day_dt, month_dt=month_dt)
        assert all(map(lambda m: m.id_sender == 1 and m.is_sent == True, _messages))
        assert len(_messages) == nres

    @pytest.mark.parametrize('code,data,toggle', [
        (200,{'toggle': True}, True),
        (200, {'toggle': False}, False),
        (404, {}, False),
    ])
    def test_get_user_content_filter(self, code, data, toggle):
        with mock.patch('requests.get') as m:
            m.return_value=MockResponse(code=code, json=data)
            _code, _toggle = MessageManager.get_user_content_filter(1)
            assert _toggle == toggle
            assert _code == code

    @pytest.mark.parametrize('exception', [
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
    ])
    def test_get_user_content_filter_error(self, exception):
        with mock.patch('requests.get') as m:
            m.side_effect = exception()
            _code, _toggle = MessageManager.get_user_content_filter(1)
            assert _toggle == False
            assert _code == 500

    @pytest.mark.parametrize('day_dt, month_dt, cf, nres', [
        (None, None, True, 2,),
        (None, None, False, 3,),
        (datetime(2022,10,10), None, False, 2),
        (None, datetime(2022,10,1), False, 3),
        (datetime(2022,10,10), datetime(2022,10,1), False, 2),
    ])
    def test_get_received_messages(self, received_list, day_dt, month_dt, cf, nres):
        print(db.session.query(Message).count())
        with mock.patch('mib.dao.message_manager.MessageManager.get_user_content_filter') as m:
            m.return_value = 200, cf
            _messages, _dict = MessageManager.get_received_messages(1, day_dt=day_dt, month_dt=month_dt)
            assert all(map(lambda m: 1 in [r.id_recipient for r in m.recipients] and m.is_sent == True and m.is_arrived == True, _messages))
            assert all(map(lambda v: not v, _dict.values()))
            assert len(_messages) == nres

    @pytest.mark.parametrize("is_sent,is_arrived,id_user,result", [
        (True, True, 1, True),
        (True, True, 2, True),
        (True, True, 3, False),
        (True, False, 1, True),
        (True, False, 2, False),
        (True, False, 3, False),
        (False, False, 1, True),
        (False, False, 2, False),
        (False, False, 3, False),
    ])
    def test_user_can_read(self, messages, is_sent, is_arrived, id_user, result):
        _message,_ = messages
        _message.is_arrived = is_arrived
        _message.is_sent = is_sent
        db.session.commit()
        assert MessageManager.user_can_read(id_user, _message) == result

    @pytest.mark.parametrize("is_sent,is_arrived,result", [
        (True, True, False),
        (False, True, False),
        (True, False, False),
        (False, False, True),
    ])
    def test_delete_draft(self, is_sent, is_arrived, result):
        _message = Message(id_sender=1, recipients=[Recipient(id_recipient=2)], is_sent=is_sent, is_arrived=is_arrived)
        db.session.add(_message)
        db.session.commit()
        assert MessageManager.delete_draft(_message) == result
        if result:
            assert db.session.query(Message).count() == 0
        else:
            db.session.delete(_message)
            db.session.commit()

    def test_send_message(self, messages):
        _message, _ = messages
        assert _message.is_sent == False
        MessageManager.send_message(_message)
        assert _message.is_sent == True

    def test_withdraw_message(self, messages):
        _message, _ = messages
        _message.is_sent == True
        db.session.commit()
        MessageManager.withdraw_message(_message)
        assert _message.is_sent == False


    @pytest.mark.parametrize("code,id_list,deep_list,diff_elem,called", [
        (200, [], [], 0, False),
        (404, [1], [[2]], 0, True),
        (200, [], [[],[],[]], 0, False),
        (200, [1], [], 1, True),
        (200, [], [[1,2],[2,3,5]], 4, True),
        (200, [1,2], [[1,2],[2,3,5]], 4, True),
    ])
    def test_retrieve_users_info(self, code, id_list, deep_list, diff_elem, called):
        _called = False
        def mock_get_fun(endpoint, timeout=5):
            inds = endpoint.find('[')
            inde = endpoint.find(']')
            print(inds)
            print(inde)
            ids = map(lambda s: int(s), endpoint[inds+1:inde].split(','))
            nonlocal _called
            _called = True
            return MockResponse(
                code=code,
                json={'recipients': [{'id': id, 'test': 'test value'} for id in ids]}
            )

        with mock.patch('requests.get', new=mock_get_fun):
            dict = MessageManager.retrieve_users_info(id_list=id_list, deep_list=deep_list)
            assert _called == called
            assert len(dict.keys()) == diff_elem
            if code == 200:
                for id in id_list:
                    assert id in dict
                    assert 'test' in dict[id]
                    assert 'test value' == dict[id]['test']
                for l in deep_list:
                    for id in l:
                        assert id in dict
                        assert 'test' in dict[id]
                        assert 'test value' == dict[id]['test']

    @pytest.mark.parametrize("exception", [
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
    ])
    def test_retrieve_users_info_error(self, exception):
        with mock.patch('requests.get') as m:
            m.side_effect = exception()
            dict = MessageManager.retrieve_users_info(id_list=[1], deep_list=[])
            assert len(dict.keys()) == 0

    def test_get_arrived_messages(self, messages):
        messages[0].delivery_date=datetime.strptime('10/10/2021 10:30', '%H:%M %d/%m/%Y')
        messages[0].is_sent = True
        messages[1].delivery_date=datetime.today() + timedelta(days=1)
        messages[1].is_sent = True

        mess = MessageManager.get_new_arrived_messages()
        assert len(mess) == 1
        assert mess[0]["id"] == messages[0].id_message


