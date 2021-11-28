from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash


db = SQLAlchemy()

class Message(db.Model):

    __tablename__ = "message"

    # id_message is the primary key that identify a message
    id_message = db.Column(db.Integer, primary_key=True, autoincrement=True)

    id_sender = db.Column(db.Integer)

    recipients = db.relationship(
        "Recipient", back_populates="message", cascade="all, delete-orphan"
    )

    body_message = db.Column(db.Unicode(256))
    img_path = db.Column(
        db.Unicode(128)
    )  # we store the path of the image in the web server
    date_of_send = db.Column(db.DateTime)

    # boolean variables that describe the state of the message
    is_sent = db.Column(db.Boolean, default=False)
    is_arrived = db.Column(db.Boolean, default=False)
    # is_notified_sender = db.Column(db.Boolean, default = False)

    # boolean flag that tells if the message must be filtered for users who resquest it
    to_filter = db.Column(db.Boolean, default=False)

    # id of the message this one is a reply for
    reply_to = db.Column(db.Integer)

    # constructor of the message object
    def __init__(self, *args, **kw):
        super(Message, self).__init__(*args, **kw)