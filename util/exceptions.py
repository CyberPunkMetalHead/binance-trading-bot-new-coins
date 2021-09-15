class ShouldNotRunException(BaseException):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class NoSuchFutureException(BaseException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)


class MissingEntryException(BaseException):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class NoBrokerResponseRetryException(BaseException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)


class InvalidReduceOnlyError(BaseException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)


class GetPriceNoneResponse(BaseException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)


class NoBrokerResponseException(BaseException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)


class AlreadyClosedException(BaseException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)


class BadGatewayException(BaseException):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ConnectionRefusedException(BaseException):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class BrokerDownException(BaseException):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
