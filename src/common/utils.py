import logging
import jwt
import hashlib
import math
from uuid import uuid4
from jinja2 import FileSystemLoader, BaseLoader, Environment as JinjaEnv
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from cryptography.fernet import Fernet

from .constants import PAGINATION, ISO8601_DATETIME_RE

log = logging.getLogger('easygds')


def gen_uuid():
    return uuid4().hex


def make_loggable_data(data):
    length = 500
    result = str(data)

    if len(result) > length:
        result = result[:length] + '...'

    return result


def log_data(mode: str,
             logger: logging.Logger = None,
             template: str = None,
             args: list = None,
             kwargs: dict = None):
    if logger:
        handler = getattr(logger, mode)
    else:
        handler = getattr(log, mode)

    if not args:
        args = []
    if not kwargs:
        kwargs = {}

    _args = [
        make_loggable_data(i)
        for i in args
    ]

    _kwargs = dict(list(map(
        lambda i: (i[0], make_loggable_data(i[1])),
        kwargs.items()
    )))

    if template:
        handler(template.format(*_args, **_kwargs))
    else:
        handler(_kwargs)


def encrypt(string, secret_key):
    if not isinstance(string, bytes):
        string = string.encode()
    fernet = Fernet(key=secret_key)
    return fernet.encrypt(string).decode()


def decrypt(token, secret_key):
    if not isinstance(token, bytes):
        token = token.encode()
    fernet = Fernet(key=secret_key)
    return fernet.decrypt(token).decode()


def mask_string(value: str,
                mask_char: str,
                percent: int,
                reverse: bool = False) -> str:
    if percent > 100:
        percent = 100

    value_length = len(value)
    mask_length = math.floor((value_length * percent) / 100)

    if reverse:
        mask_offset = 0
    else:
        mask_offset = value_length - mask_length
    value_list = list(value)
    value_list[
    mask_offset: mask_offset + mask_length] = mask_char * mask_length
    return ''.join(value_list)


def hash_string(string, mode='sha256'):
    hash_handler = getattr(hashlib, mode, None)
    if not hash_handler:
        raise Exception('UnsupportedHashMode')

    if not isinstance(string, bytes):
        string = string.encode()

    return hash_handler(string).hexdigest()


def find_list_element_obj(array: list,
                          key: str,
                          value: any) -> tuple:
    result = None
    index = None
    for i, item in enumerate(array):
        if isinstance(item, dict):
            v = item[key]
        elif isinstance(item, object):
            v = getattr(item, key)
        else:
            v = item
        if v != value:
            continue

        result = item
        index = i
        break
    return result, index


def get_now(timestamp=False):
    result = datetime.utcnow()
    result.replace(tzinfo=timezone.utc)
    if timestamp:
        return result.timestamp()
    return result


def paginate(query, page=None, per_page=None):
    if not page:
        page = PAGINATION['page']
    if not per_page:
        per_page = PAGINATION['per_page']
    return query.offset((page - 1) * per_page).limit(per_page)


def get_fixed_timezone(offset) -> timezone:
    """Return a tzinfo instance with a fixed offset from UTC."""
    if isinstance(offset, timedelta):
        offset = offset.total_seconds() // 60
    sign = "-" if offset < 0 else "+"
    hhmm = "%02d%02d" % divmod(abs(offset), 60)
    name = sign + hhmm
    return timezone(timedelta(minutes=offset), name)


def iso_string_to_datetime(value: str, *args, **kwargs):
    """Parse a string and return a datetime.datetime.

    This function supports time zone offsets. When the input contains one,
    the output uses a timezone with a fixed offset from UTC.
    """
    match = ISO8601_DATETIME_RE.match(value)
    if not match:
        raise ValueError("Not a valid ISO8601-formatted datetime string")
    kw = match.groupdict()
    kw["microsecond"] = kw["microsecond"] and kw["microsecond"].ljust(6,
                                                                      "0")
    tzinfo = kw.pop("tzinfo")
    if tzinfo == "Z":
        tzinfo = timezone.utc
    elif tzinfo is not None:
        offset_mins = int(tzinfo[-2:]) if len(tzinfo) > 3 else 0
        offset = 60 * int(tzinfo[1:3]) + offset_mins
        if tzinfo[0] == "-":
            offset = -offset
        tzinfo = get_fixed_timezone(offset)
    kw = {k: int(v) for k, v in kw.items() if v is not None}
    kw["tzinfo"] = tzinfo
    return datetime(**kw)


def make_jwt_token(secret_key, expire_time=3600, **kwargs):
    now = datetime.now()

    expire = now + timedelta(seconds=expire_time)

    payload = OrderedDict(
        exp=expire,
        **kwargs
    )
    return jwt.encode(payload, secret_key, algorithm='HS256').decode()


def decode_jwt_token(token, secret_key, verify_expire=False):
    try:
        token_data = jwt.decode(token, secret_key,
                                options={'verify_exp': verify_expire})

    except Exception as e:
        return None
    return token_data


def get_list_item(key, value, list_item: list):
    result = None
    for i in list_item:
        if key not in i:
            continue
        v = i[key]
        if v != value:
            continue
        result = i
        break
    return result


def gen_next_version(last: str = None,
                     version_length: int = 4) -> str:
    if not last:
        last = 0
    else:
        last = last.replace('.', '')
        last = int(last)

    new_version = str(last + 1)
    if len(new_version) < version_length:
        new_version = '0' * (version_length - len(new_version)) + new_version

    new_version = list(new_version)

    return '.'.join(new_version)


def convert_string_to_datetime(string, formats):
    value = None
    for datetime_format in formats:
        try:
            value = datetime.strptime(string, datetime_format)
            break
        except ValueError:
            continue

    return value


def change_datetime_format(string, from_format, to_format):
    datetime_obj = convert_string_to_datetime(string, [from_format])
    return datetime_obj.strftime(to_format)


def find_in_list(array: list,
                 values: dict):
    first_item = array[0]

    def check_function(item):
        match = True
        for k, v in values.items():
            if isinstance(first_item, dict):
                if k not in item:
                    match = False
                    break
                item_value = item[k]
            else:
                if not hasattr(item, k):
                    match = False
                    break
                item_value = getattr(item, k)
            if v != item_value:
                match = False
                break
        return match

    query = list(filter(lambda x: check_function(x), array))
    if not len(query):
        return None, None
    result = query[0]
    return result, array.index(result)


def gen_html(content, data, template_dir=None):
    if template_dir:
        loader = FileSystemLoader(template_dir)
    else:
        loader = BaseLoader()

    template_handler = JinjaEnv(
        loader=loader).from_string(content)

    return template_handler.render(
        **data
    )


def get_nested_level(array: list = None, level: int = 0):
    if not array:
        return level
    first_elem = array[0]
    if not isinstance(first_elem, list):
        return level
    level += 1
    return get_nested_level(first_elem, level)
