import untangle


class FimCodeList(object):
    def __init__(self, urn):
        self.xml = untangle.parse(urn)
