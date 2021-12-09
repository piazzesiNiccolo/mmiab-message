import pytest
import os
import mock
import io
import base64
from werkzeug.datastructures import FileStorage
from mib.dao.utils import Utils
from mib.models.message import Message
from uuid import uuid4
from tempfile import mkstemp


class TestUtils:
    def test_load_image_none(self):
        message = Message()
        image = Utils.load_message_image(message)
        assert image["name"] == None
        assert image["data"] == ""
        assert image["type"] == ""

    def test_load_image_not_found(self):
        filename = str(uuid4()) + ".png"
        message = Message(img_path=filename)
        image = Utils.load_message_image(message)
        assert image["name"] == filename
        assert image["data"] == ""
        assert image["type"] == ""

    def test_load_image_ok(self):
        dirname = "mib/static/assets/"
        tfd, fullpath = mkstemp(dir=dirname, suffix=".png")
        filename = os.path.basename(fullpath)
        with os.fdopen(tfd, "wb") as temp:
            temp.write(b"many data")

        message = Message(img_path=filename)
        with mock.patch("os.path.join") as m:
            m.return_value = dirname + filename
            image = Utils.load_message_image(message)
            assert image["name"] == filename
            assert b"many data" == base64.b64decode(image["data"].encode("utf-8"))
            assert image["type"] == "png"

        os.remove(fullpath)

    def test_save_image_empty(self):
        assert Utils.save_message_image(None) == None

    def test_save_image_ok(self):
        filename = "test.png"
        with mock.patch("os.path.join") as m:
            fake_path = "mib/static/assets/" + filename
            m.return_value = fake_path
            name = Utils.save_message_image(
                {
                    "data": base64.b64encode(b"many data").decode("utf-8"),
                    "name": filename,
                }
            )
            assert name.endswith(filename)
            with open(fake_path, "rb") as file:
                assert file.read() == b"many data"
            os.remove(fake_path)

    def test_delete_image_none(self):
        message = Message()
        assert not Utils.delete_message_image(message)

    def test_delete_image_not_found(self):
        filename = str(uuid4()) + ".png"
        message = Message(img_path=filename)
        assert not Utils.delete_message_image(message)

    def test_delete_image_ok(self):
        dirname = "mib/static/assets/"
        tfd, fullpath = mkstemp(dir=dirname, suffix=".png")
        filename = os.path.basename(fullpath)
        with os.fdopen(tfd, "wb") as temp:
            temp.write(b"many data")

        message = Message(img_path=filename)
        with mock.patch("os.path.join") as m:
            m.return_value = dirname + filename
            assert Utils.delete_message_image(message)
            with pytest.raises(FileNotFoundError):
                open(dirname + filename, "r")
