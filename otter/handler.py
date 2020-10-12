
class Echo:
    def get(self, query):
        return "query=%s" % (query)

    def post(self, query, data):
        return "query=%s, data=%s" % (query, data)

