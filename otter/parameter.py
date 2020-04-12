
from pytils import check


class Extractor:
    def __init__(self, name, default, plural=False, canonicalize=lambda v: v):
        self.name = check.check_not_empty(name)
        self.default = default
        self.plural = check.check_one_of(plural, [True, False])
        self.canonicalize = canonicalize
        self.key = self.name if not self.plural else "%s[]" % self.name

    def extract(self, query):
        value = self.default

        if self.key in query:
            if self.plural:
                value = [self.canonicalize(v) for v in query[self.key]]
            else:
                value = self.canonicalize(query[self.key][0])

        return value


class Value:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)

