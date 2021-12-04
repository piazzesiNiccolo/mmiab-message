import pytest
from mib import db
from mib.dao.recipient_manager import RecipientManager
from mib.models.message import Message
from mib.models.recipient import Recipient

class TestRecipientManager:

    @pytest.mark.parametrize("is_none,recipients,id,res_none", [
        (False, [1,2,3], 1, False),
        (False, [1,2,3], 4, True),
        (False, [], 1, True),
        (True, [], 1, True),
    ])
    def test_retrieve_by_id(self, is_none, recipients, id, res_none):
        if is_none:
            assert RecipientManager.retrieve_recipient_by_id(None, id) == None
        else:
            _message = Message(recipients=[Recipient(id_recipient=i) for i in recipients])
            if res_none:
                assert RecipientManager.retrieve_recipient_by_id(_message, id) == None
            else:
                assert RecipientManager.retrieve_recipient_by_id(_message, id).id_recipient == id

    @pytest.mark.parametrize("is_none,recipients", [
        (False, [1,2,3]),
        (False, []),
        (True, []),
    ])
    def test_get_recipients(self, is_none, recipients):
        if is_none:
            assert RecipientManager.get_recipients(None) == []
        else:
            _message = Message(recipients=[Recipient(id_recipient=i) for i in recipients])
            assert RecipientManager.get_recipients(_message) == recipients

    @pytest.mark.parametrize("is_none,recipients,id,result", [
        (False, [1,2,3], 1, True),
        (False, [1,2,3], 4, False),
        (False, [], 1, False),
        (True, [], 1, False),
    ])
    def test_is_recipient(self, is_none, recipients, id, result):
        if is_none:
            assert RecipientManager.is_recipient(None, id) == result
        else:
            _message = Message(recipients=[Recipient(id_recipient=i) for i in recipients])
            assert RecipientManager.is_recipient(_message, id) == result

    @pytest.mark.parametrize("is_none,recipients,id,old_value,result", [
        (False, [1, 2, 3], 1, True, True),
        (False, [1, 2, 3], 1, False, False),
        (False, [1, 2, 3], 4, False, False),
        (False, [1, 2, 3], 4, True, False),
        (False, [], 1, False, False),
        (False, [], 1, True, False),
        (True, [], 1, False, False),
    ])
    def test_has_opened(self, is_none, recipients, id, old_value, result):
        if is_none:
            assert RecipientManager.has_opened(None, id) == result
        else:
            rcps = [Recipient(id_recipient=i, has_opened=old_value) for i in recipients]
            _message = Message(recipients=rcps)
            assert RecipientManager.has_opened(_message, id) == result
            if len(recipients) > 0 and id in recipients:
                assert next(r for r in rcps if r.id_recipient == id).has_opened == True

    @pytest.mark.parametrize("is_none,recipients,id,is_arrived,result", [
        (False, [1, 2, 3], 1, True, True),
        (False, [1, 2, 3], 1, False, False),
        (False, [1, 2, 3], 4, True, False),
        (False, [1, 2, 3], 4, False, False),
        (False, [], 1, True, False),
        (False, [], 1, False, False),
        (True, [], 1, False, False),
    ])
    def test_can_delete_read(self, is_none, recipients, id, is_arrived, result):
        if is_none:
            assert RecipientManager.can_delete_read(None, id) == result
        else:
            _message = Message(recipients=[Recipient(id_recipient=i) for i in recipients], is_arrived=is_arrived)
            assert RecipientManager.can_delete_read(_message, id) == result

    @pytest.mark.parametrize("is_none,recipients,id,has_opened,result", [
        (False, [1, 2, 3], 1, True, True),
        (False, [1, 2, 3], 1, False, False),
        (False, [1, 2, 3], 4, True, False),
        (False, [1, 2, 3], 4, False, False),
        (False, [], 1, True, False),
        (False, [], 1, False, False),
        (True, [], 1, False, False),
    ])
    def test_delete_read_message(self, is_none, recipients, id, has_opened, result):
        if is_none:
            assert RecipientManager.delete_read_message(None, id) == False
        else:
            rcps = [Recipient(id_recipient=i, has_opened=has_opened) for i in recipients]
            _message = Message(recipients=rcps)
            assert RecipientManager.delete_read_message(_message, id) == result
            if result:
                assert next(r for r in rcps if r.id_recipient == id).read_deleted == True

    @pytest.mark.parametrize("replying,recipients,check", [
        (False, [1, 2, 3], [1, 2, 3]),
        (False, [1, 1, 2, 3], [1, 2, 3]),
        (False, [], []),
        (True, [2, 3], [1, 2, 3]),
        (True, [1, 2, 3], [1, 2, 3]),
    ])
    def test_set_recipients_no_reply(self, messages, recipients, check, replying):
        m1, m2 = messages
        if replying:
            m2.reply_to = m1.id_message
            db.session.commit()
        RecipientManager.set_recipients(m2, recipients, replying=replying)
        assert all(map(lambda r: r.id_recipient in check, m2.recipients))
        assert len(m2.recipients) == len(check)



