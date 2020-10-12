
import json
import re

import pytils.override

from otter import error


def to_string(data):
    try:
        pytils.override.patch_json_encode()
        return json.dumps(data, indent=4, separators=(", ", ": "))
    finally:
        pytils.override.unpatch_json_encode()


def from_string(data):
    try:
        json_string = _clean_json(data)
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise error.BadRequest("Error decoding json: %s" % str(e))


# Basic support for comments & commas extension on top of json.
# Won't be perfect, but it works for our use cases.
# Notes:
#   https://hjson.github.io/
#       Surprisingly didn't support my simple test example.
#   https://pypi.org/project/jsoncomment/
#       Is unsupported?  Could not find source or documentation.
#   https://gist.github.com/liftoff/ee7b81659673eca23cd9fc0d8b8e68b7
#       Solution here is based off this gist, but much simpler.
REGEX_COMMENT_MULTILINE = re.compile(r"/\*.*?\*/", re.DOTALL | re.MULTILINE)
REGEX_COMMENT = re.compile(r"//.*?([\"{}\[\],])", re.DOTALL | re.MULTILINE)
REGEX_OBJECT_COMMA = re.compile(r"(,)\s*}")
REGEX_LIST_COMMA = re.compile(r"(,)\s*\]")


def _clean_json(json_string):
    out = json_string

    # Remove multi-line comments "/* .. */".
    out = re.sub(REGEX_COMMENT_MULTILINE, "", out)

    # Remove trailing comments "// ..".
    out = re.sub(REGEX_COMMENT, "\\1", out)

    # Remove trailing object commas '},'.
    out = re.sub(REGEX_OBJECT_COMMA, "}", out)

    # Remove trailing list commas '],'.
    return re.sub(REGEX_LIST_COMMA, "]", out)

