from mib.background import _arrived_messages
from datetime import datetime, timedelta


class TestBackgroundTasks:
    def test_arrived_messages(self, messages):
        messages[0].delivery_date = datetime.strptime(
            "10:30 10/10/2021", "%H:%M %d/%m/%Y"
        )
        messages[0].is_sent = True
        messages[1].delivery_date = datetime.today() + timedelta(days=1)
        messages[1].is_sent = True
        mess = _arrived_messages()
        assert len(mess["notifications"]) == 1
        assert mess["notifications"][0]["id_message"] == messages[0].id_message
