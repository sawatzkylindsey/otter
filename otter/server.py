
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
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

from pytils.log import user_log


class ServerHandler(BaseHTTPRequestHandler):
    API_KIND = "api"
    RESOURCE_KIND = "resource"

    @error.handlesafely
    def do_GET(self):
        (kind, path, data) = self._request()

        if kind == ServerHandler.API_KIND:
            handler = path.replace("/", "_")

            if handler in self.server.handlers:
                # Only log requests that go to the handlers to reduce logging noise.
                logging.debug("GET %s: %s" % (path, data))
                out = self.server.handlers[handler].get(data)

                if out == None:
                    out = {}

                self._set_headers("application/json")

                if hasattr(out, "as_json"):
                    out = out.as_json()

                return self._response_content(json.dumps(out))
        elif kind == ServerHandler.RESOURCE_KIND:
            # The request is for a file on the file system.
            file_path = os.path.join(".", self.server.resource_path, path)

            # Some systems allow for relative paths to pass through urllib.
            # Make sure the constructed path is a subpath of the server's resource path.
            if not os.path.abspath(file_path).startswith(os.path.abspath(os.path.join(".", self.server.resource_path))):
                raise error.NotFound(path)

            if os.path.exists(file_path) and os.path.isfile(file_path):
                mimetype, _ = mimetypes.guess_type(path)

                if mimetype is None:
                    mimetype = "text/plain"

                self._set_headers(mimetype)
                encode = "text" in mimetype
                return self._response_file(file_path, encode)

        raise error.NotFound(path)

    def _response_file(self, file_path, encode=True):
        if encode:
            with open(file_path, "r") as fh:
                self._response_content(fh.read())
        else:
            with open(file_path, "rb") as fh:
                self.wfile.write(fh.read())

        return None

    def _response_content(self, content):
        self.wfile.write(content.encode("utf-8"))
        return None

    def _request(self):
        url = urllib.parse.urlparse(self.path)
        request_data = urllib.parse.parse_qs(url.query)
        request_path = urllib.parse.unquote(url.path[1:])
        request_type = ServerHandler.RESOURCE_KIND

        if request_path.startswith(self.server.api_root):
            request_type = ServerHandler.API_KIND
            request_path = request_path.replace(self.server.api_root, "")

        return (request_type, request_path, request_data)

    def _set_headers(self, content_type, others={}):
        self.send_response(200)
        self.send_header('Content-type', content_type)

        for key, value in others.items():
            self.send_header(key, value)

        self.end_headers()


def run_server(port, api_root, resource_path, handler_map):
    class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
        pass

    server_address = ('', port)
    httpd = ThreadingHTTPServer(server_address, ServerHandler)
    httpd.daemon_threads = True
    httpd.api_root = api_root if api_root.endswith("/") else "%s/" % api_root
    httpd.resource_path = resource_path
    httpd.handlers = handler_map
    user_log.info('Starting httpd %d...' % port)
    httpd.serve_forever()

