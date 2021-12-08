import json
import logging

from mib.dao.manager import Manager
from mib import db
from mib.models.recipient import Recipient
from mib.models.message import Message

def delete_recipients_user_not_exists(message):
    if message["type"] == "message":
        usr = json.loads(message["data"])
        id = usr.get("user_id")
        db.session.query(Recipient).filter(Recipient.id_recipient == id).delete()
        db.session.query(Message).filter(Message.id_sender == id).update({
            Message.id_sender:0
        })
        Manager.update()
        logging.info(f"removed participant with user_id {id}")
