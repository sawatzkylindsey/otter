
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import mimetypes
import os
import pdb
from socketserver import ThreadingMixIn
import sys
from threading import Thread
import urllib

from otter import error
from otter import handler
from otter import serializer

from pytils.log import user_log


class ServerHandler(BaseHTTPRequestHandler):
    API_KIND = "api"
    RESOURCE_KIND = "resource"

    @error.handlesafely
    def do_GET(self):
        self._check_whitelist()
        (kind, path, handler, query, _, _) = self._request()

        if kind == ServerHandler.API_KIND:
            if handler in self.server.handlers:
                # Only log requests that go to the handlers to reduce logging noise.
                logging.debug("GET %s: %s" % (path, query))

                if not hasattr(self.server.handlers[handler], "get"):
                    raise error.NotAllowed(path, "get")

                out = self.server.handlers[handler].get(query)

                if out == None:
                    out = {}


                if hasattr(out, "as_json"):
                    out = out.as_json()

                response = serializer.to_string(out)
                self._set_headers()
                self._response_content(response)
                # return to avoid falling through to the final raise statement
                return
        elif kind == ServerHandler.RESOURCE_KIND:
            # The request is for a file on the file system.
            file_path = os.path.join(".", self.server.resource_path, path[1:])

            # Some systems allow for relative paths to pass through urllib.
            # Make sure the constructed path is a subpath of the server's resource path.
            if not os.path.abspath(file_path).startswith(os.path.abspath(os.path.join(".", self.server.resource_path))):
                raise error.NotFound(path)

            if os.path.exists(file_path) and os.path.isfile(file_path):
                mimetype, _ = mimetypes.guess_type(path)

                if mimetype is None:
                    mimetype = "text/plain"

                encode = "text" in mimetype
                self._set_headers(mimetype)
                self._response_file(file_path, encode)
                # return to avoid falling through to the final raise statement
                return

        raise error.NotFound(path)

    @error.handlesafely
    def do_POST(self):
        self._check_whitelist()
        (kind, path, handler, query, data, content) = self._request()

        if kind == ServerHandler.API_KIND:
            if handler in self.server.handlers:
                # Only log requests that go to the handlers to reduce logging noise.
                logging.debug("POST %s: %s | %s" % (path, query, truncate(content)))

                if not hasattr(self.server.handlers[handler], "post"):
                    raise error.NotAllowed(path, "post")

                out = self.server.handlers[handler].post(query, data)

                if out == None:
                    out = {}

                if hasattr(out, "as_json"):
                    out = out.as_json()

                response = serializer.to_string(out)
                self._set_headers()
                self._response_content(response)
                # return to avoid falling through to the final raise statement
                return

        raise error.NotFound(path)

    def _response_file(self, file_path, encode=True):
        if encode:
            with open(file_path, "r") as fh:
                self._response_content(fh.read())
        else:
            with open(file_path, "rb") as fh:
                self.wfile.write(fh.read())

    def _response_content(self, content):
        self.wfile.write(content.encode("utf-8"))

    def _request(self):
        url = urllib.parse.urlparse(self.path)
        request_type = ServerHandler.RESOURCE_KIND
        request_path = urllib.parse.unquote(url.path[1:])
        request_handler = None
        request_query = urllib.parse.parse_qs(url.query)
        request_data = None

        if request_path.startswith(self.server.api_root):
            request_type = ServerHandler.API_KIND
            request_handler = request_path.replace(self.server.api_root, "")

        if "Content-Length" in self.headers:
            content_length = int(self.headers["Content-Length"])
            content = self.rfile.read(content_length).decode("utf-8")
            request_data = serializer.from_string(content)
        else:
            content = None

        return (request_type, "/" + request_path, request_handler, request_query, request_data, content)

    def _set_headers(self, content_type=None, others={}):
        self.send_response(200)
        self.send_header('Content-Type', "application/json" if content_type is None else content_type)

        for key, value in others.items():
            self.send_header(key, value)

        self.end_headers()

    def _check_whitelist(self):
        ip_address = self.client_address[0]

        if self.server.ip_whitelist is not None \
            and ip_address not in self.server.ip_whitelist:
            raise error.Forbidden()


def run_server(port, api_root, resource_path, handler_map, ip_whitelist=["127.0.0.1"]):
    class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
        pass

    server_address = ('', port)
    httpd = ThreadingHTTPServer(server_address, ServerHandler)
    httpd.daemon_threads = True
    httpd.api_root = api_root if api_root.endswith("/") else "%s/" % api_root
    httpd.resource_path = resource_path if resource_path.endswith("/") else "%s/" % resource_path
    httpd.handlers = handler_map
    httpd.ip_whitelist = ip_whitelist
    user_log.info('Starting httpd %d...' % port)
    httpd.serve_forever()


def truncate(value):
    if value is None:
        return None

    v = str(value)

    if len(v) > 100:
        return v[:97] + "..."

    return v

