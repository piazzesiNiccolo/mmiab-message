import json
import pytest
from mib.events.callbacks import delete_recipients_user_not_exists
from mib.models.message import Message
from mib.models.recipient import Recipient
from mib import db


class TestCallbacks:
    @pytest.mark.parametrize("type", ["foo", "message"])
    def test_delete_user_not_exists(self, type, messages):
        rec = Recipient()
        msg = {"type": type, "data": json.dumps({"user_id": 1})}
        rec = Recipient(id_recipient=1, message=messages[0])
        db.session.add(rec)
        db.session.commit()
        assert (
            db.session.query(Recipient).filter(Recipient.id_recipient == 1).first()
            is not None
        )
        delete_recipients_user_not_exists(msg)
        if type == "foo":
            assert (
                db.session.query(Recipient).filter(Recipient.id_recipient == 1).first()
                is not None
            )
        else:
            assert (
                db.session.query(Recipient).filter(Recipient.id_recipient == 1).first()
                is None
            )
            assert Message.query.get(1).id_sender == 0
