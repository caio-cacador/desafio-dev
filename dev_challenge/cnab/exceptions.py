
class Error(Exception):
    """Base class for other exceptions"""
    pass


class InvalidTransactionType(Error):
    """Raised when the transaction type is incorrect"""
    pass
