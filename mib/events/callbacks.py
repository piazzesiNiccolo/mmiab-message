import json
import logging

from mib.dao.manager import Manager
from mib import db
from mib.models.recipient import Recipient

def delete_recipients_user_not_exists(message):
    if message["type"] == "message":
        usr = json.loads(message["data"])
        id = usr.get("user_id")
        db.session.query(Recipient).filter(Recipient.id_recipient == id).delete()
        Manager.update()
        logging.info(f"removed participant with user_id {id}")
