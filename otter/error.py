
import json
import logging
import pdb
import traceback


class HttpError(Exception):
    def as_json(self, code):
        return {
            "error": {
                "code": code,
                "message": repr(self),
            }
        }


class Invalid(HttpError):
    def __init__(self, reason):
        self.reason = reason

    def __repr__(self):
        return "Invalid: %s" % self.reason


class NotFound(HttpError):
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return "NotFound: %s" % self.path


class NotAllowed(HttpError):
    def __init__(self, path, method):
        self.path = path
        self.method = method

    def __repr__(self):
        return "NotAllowed: %s %s" % (self.method, self.path)


MAPPING = {
    Invalid: 400,
    NotFound: 404,
    NotAllowed: 405,
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
            code = 500

            if error_type in MAPPING:
                code = MAPPING[error_type]

            self.send_response(code)

            if isinstance(error, HttpError):
                self.send_header('Content-Type', "application/json")
                self.wfile.write(json.dumps(error.as_json(code)).encode("utf-8"))
            else:
                self.wfile.write(error_message.encode("utf-8"))

            self.end_headers()

    return wrapper

