# -*- coding: utf-8 -*-
#



__author__ = "Epsirom"


class BaseError(Exception):

    def __init__(self, code, msg):
        super(BaseError, self).__init__(msg)
        self.code = code
        self.msg = msg

    def __repr__(self):
        return '[ERRCODE=%d] %s' % (self.code, self.msg)


class InputError(BaseError):

    def __init__(self, msg):
        super(InputError, self).__init__(1, msg)


class LogicError(BaseError):

    def __init__(self, msg):
        super(LogicError, self).__init__(2, msg)


class ValidateError(BaseError):

    def __init__(self, msg):
        super(ValidateError, self).__init__(3, msg)


class NotExistError(BaseError):

    def __init__(self, msg):
        super(NotExistError, self).__init__(4, msg)


class NotAvailableError(BaseError):

    def __init__(self, msg):
        super(NotAvailableError, self).__init__(5, msg)


class TransactionError(BaseError):

    def __init__(self, msg):
        super(TransactionError, self).__init__(6, msg)


class NotBindError(BaseError):

    def __init__(self, msg):
        super(NotBindError, self).__init__(7, msg)
