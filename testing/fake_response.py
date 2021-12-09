class MockResponse:
    def __init__(self, code=200, json={}):
        self.status_code = code
        self.json_data = json

    def json(self):
        return self.json_data
