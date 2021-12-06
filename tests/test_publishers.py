import pytest
from mib.events.publishers import EventPublishers

class TestPublishers:

    @pytest.mark.parametrize("key, ret",[ 
        ("users",0),
        ("foo",None)
    ])
    def test_publish_withdraw_points(self, key, ret):
        payload = {
            key: [{
                "id":1,
                "points":-1
            },
            {
                "id":2,
                "points":-1
            }]
        }
        assert EventPublishers.publish_withdraw_points(payload) == ret
    
    @pytest.mark.parametrize("key, ret",[ 
        ("notifications",0),
        ("foo",None)
    ])
    def test_publish_notify(self, key, ret):
        payload = {
            key:[{ 
                "id_message":5,
                "id_user":1,
                "is_notified":False,
                "for_recipient":True,
                "for_sender":False,
                "for_lottery":False,
                "from_recipient": None
            }]
        }
        assert EventPublishers.publish_add_notify(payload) == ret