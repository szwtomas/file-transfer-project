import re

VALID_PATH_REGEX = "^(\.\.\/(?:\.\.\/)*)?(?!.*?\/\/)(?!(?:.*\/)?\.+(?:\/|$)).+$"

def regex_matches(s):
    return bool(re.match(VALID_PATH_REGEX, s))

def is_valid_path_syntax(path):
    return regex_matches(path)