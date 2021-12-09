from mib import db


class Recipient(db.Model):
    """Representation of Recipient model."""

    __tablename__ = "Recipient"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_message = db.Column(db.ForeignKey("Message.id_message"))
    id_recipient = db.Column(db.Integer)
    # true if the recipient has opened the message
    has_opened = db.Column(db.Boolean, default=False)
    # true if the recipient has deleted the read message
    read_deleted = db.Column(db.Boolean, default=False)
    message = db.relationship("Message")

    def __init__(self, *args, **kw):
        super(Recipient, self).__init__(*args, **kw)

    def set_id_recipient(self, id_recipient: int):
        self.id_recipient = id_recipient

    def set_has_opened(self, has_opened: bool):
        self.has_opened = has_opened

    def set_read_deleted(self, read_deleted):
        self.read_deleted = read_deleted
