from mib import db

class Recipient(db.Model):

    __tablename__ = "recipient"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_message = db.Column(db.ForeignKey("Message.id_message"))
    id_recipient = db.Column(db.Integer)
    # true if the recipient has opened the message
    has_opened = db.Column(db.Boolean, default=False)
    # true if the recipient has deleted the read message
    read_deleted = db.Column(db.Boolean, default=False)
    message = db.relationship("Message")


