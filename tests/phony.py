class Client:
    def __init__(self, url, request_responses):
        self.url = url
        self.reqres = request_responses

    def get(self, route):
        return self.reqres['{}/{}'.format(self.url, route)]
