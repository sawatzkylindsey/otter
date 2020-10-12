
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
        return pytils.override.extended_loads(data)
    except json.JSONDecodeError as e:
        raise error.BadRequest("Error decoding json: %s" % str(e))

