'''Simple exceptions for the :py:mod:`qgen module`

'''

class QGenException(Exception):
    """Base for other exceptions
    """
    pass

class QGenStopException(QGenException):
    """Called when ``halt_on_errors`` is set to True
    """
    pass

class QGenNoQueriesException(QGenException):
    """Called when there are no allowed queries
    """
    pass
