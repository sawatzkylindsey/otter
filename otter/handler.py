
class Echo:
    def get(self, query):
        return str(query)

    def post(self, query, data):
        return str((query, data))

