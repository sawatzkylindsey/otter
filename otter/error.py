
import json
import logging
import pdb
import traceback


class HttpError(Exception):
    def __init__(self, code):
        super().__init__()
        self.code = code

    def as_json(self):
        return {
            "error": {
                "code": self.code,
                "message": repr(self),
            }
        }


class BadRequest(HttpError):
    def __init__(self, reason):
        super().__init__(400)
        self.reason = reason

    def __repr__(self):
        return "BadRequest: %s" % self.reason


class NotFound(HttpError):
    def __init__(self, path):
        super().__init__(404)
        self.path = path

    def __repr__(self):
        return "NotFound: %s" % self.path


class NotAllowed(HttpError):
    def __init__(self, path, method):
        super().__init__(405)
        self.path = path
        self.method = method

    def __repr__(self):
        return "NotAllowed: %s %s" % (self.method, self.path)


def handlesafely(function):
    def wrapper(self):
        try:
            function(self)
        except Exception as error:
            error_type = type(error)
            error_message = repr(error)
            traceback_message = "".join(traceback.format_exception(error_type, error, error.__traceback__, chain=False)).strip()
            logging.error("Handling %s.%s\n%s" % (error_type.__module__, error_message, traceback_message))

            if isinstance(error, HttpError):
                self.send_response(error.code)
            else:
                self.send_response(500)

            if isinstance(error, HttpError):
                self.send_header('Content-Type', "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(error.as_json()).encode("utf-8"))
            else:
                self.send_header('Content-Type', "text/plain")
                self.end_headers()
                self.wfile.write(error_message.encode("utf-8"))

    return wrapper

