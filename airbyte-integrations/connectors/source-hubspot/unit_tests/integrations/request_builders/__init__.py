import abc


class AbstractRequestBuilder:
    @abc.abstractmethod
    def build(self):
        pass
