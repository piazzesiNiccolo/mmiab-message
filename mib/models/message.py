from datetime import datetime

from mib import db


class Message(db.Model):

    ## The name of the table that we explicitly set
    __tablename__ = "Message"

    # A list of fields to be serialized
    SERIALIZE_LIST = [
        "id_message",
        "id_sender",
        "recipients",
        "message_body",
        "img_path",
        "delivery_date",
        "is_sent",
        "is_arrived",
        "to_filter",
        "reply_to",
    ]

    # id_message is the primary key that identify a message
    id_message = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_sender = db.Column(db.Integer)
    recipients = db.relationship(
        "Recipient", back_populates="message", cascade="all, delete-orphan"
    )
    message_body = db.Column(db.Unicode(256))
    img_path = db.Column(
        db.Unicode(128)
    )  # we store the path of the image in the web server
    delivery_date = db.Column(db.DateTime)
    # boolean variables that describe the state of the message
    is_sent = db.Column(db.Boolean, default=False)
    is_arrived = db.Column(db.Boolean, default=False)
    # boolean flag that tells if the message must be filtered for users who resquest it
    to_filter = db.Column(db.Boolean, default=False)
    # id of the message this one is a reply for
    reply_to = db.Column(db.Integer)

    # constructor of the message object
    def __init__(self, *args, **kw):
        super(Message, self).__init__(*args, **kw)

    def set_id_sender(self, id_sender: int):
        self.id_sender = id_sender

    def set_message_body(self, message_body):
        self.message_body = message_body

    def set_img_path(self, img_path: str):
        if img_path != None:
            self.img_path = img_path

    def set_delivery_date(self, delivery_date: datetime):
        self.delivery_date = delivery_date

    def set_is_sent(self, is_sent: bool):
        self.is_sent = is_sent

    def set_is_arrived(self, is_arrived: bool):
        self.is_arrived = is_arrived

    def set_to_filter(self, to_filter: bool):
        self.to_filter = to_filter

    def set_reply_to(self, reply_to: int):
        if reply_to is not None:
            self.reply_to = reply_to

    def serialize(self):
        _dict = dict([(k, self.__getattribute__(k)) for k in self.SERIALIZE_LIST])
        if self.delivery_date is not None:
            _dict["delivery_date"] = self.delivery_date.strftime("%H:%M %d/%m/%Y")
        else:
            del _dict["delivery_date"]
        _dict["recipients"] = [rcp.id_recipient for rcp in self.recipients]
        return _dict
