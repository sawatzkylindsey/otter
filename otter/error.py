
import logging
import pdb
import traceback


class NotFound(Exception):
    def __init__(self, msg, origin=None):
        self.msg = msg
        self.origin = origin

    def __repr__(self):
        return "NotFound: %s" % self.msg


class Invalid(Exception):
    def __init__(self, msg, origin=None):
        self.msg = msg
        self.origin = origin

    def __repr__(self):
        return "Invalid: %s" % self.msg


MAPPING = {
    NotFound: 404,
    Invalid: 400
}


def handlesafely(function):
    def wrapper(self):
        try:
            function(self)
        except Exception as error:
            error_type = type(error)
            error_message = repr(error)
            traceback_message = "".join(traceback.format_exception(error_type, error, error.__traceback__, chain=False)).strip()
            logging.error("Handling %s.%s\n%s" % (error_type.__module__, error_message, traceback_message))

            if error_type in MAPPING:
                self.send_error(MAPPING[error_type], error_message)
            else:
                self.send_error(500, error_message)

    return wrapper

