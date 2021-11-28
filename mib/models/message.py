from werkzeug.security import generate_password_hash, check_password_hash

from mib import db

class Message(db.Model):

    ## The name of the table that we explicitly set
    __tablename__ = "message"

    # A list of fields to be serialized
    SERIALIZE_LIST = [
        'id_message', 
        'id_sender', 
        'recipients',
        'body_message',
        'img_path',
        'date_of_send',
        'is_sent',
        'is_arrived',
        'to_filter',
        'reply_to',
    ]
    
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

    def serialize(self):
        _dict = dict([(k, self.__getattribute__(k)) for k in self.SERIALIZE_LIST])
        _dict['date_of_send'] = self.date_of_send.strftime('%d/%m/%Y')
        return _dict