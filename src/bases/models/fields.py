import re
import datetime
import typing
import inspect
from werkzeug.datastructures import FileStorage
from werkzeug.wsgi import LimitedStream

from src.common.constants import (PHONE_REGEX, )

from .errors import ValidationError, InvalidParams

EXCLUDE = 'EXCLUDE'
INCLUDE = 'INCLUDE'
RAISE = 'RAISE'


class Field(object):
    def __init__(self,
                 required: bool = False,
                 default: any = None,
                 validator: typing.Callable = None
                 ):
        self.required = required
        self.default = default
        self.validator = validator

    def get_default(self):
        if callable(self.default):
            return self.default()
        return self.default

    def validate(self, value):
        if self.validator:
            ok, msg = self.validator(value)
            if not ok:
                raise ValidationError(message=msg)

    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value


class String(Field):
    def __init__(self, max_length=None, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length

    def validate(self, value):
        super().validate(value)
        if not isinstance(value, str):
            raise ValidationError(message='Not a valid string')

        if self.max_length:
            if len(value) > self.max_length:
                raise ValidationError(
                    message=f'Exceeds maximum length: {self.max_length}'
                )


class Boolean(Field):
    def validate(self, value):
        super().validate(value)

        if not isinstance(value, bool):
            raise ValidationError(
                message='Not a valid bool'
            )


class Integer(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def deserialize(self, value):
        value = super().deserialize(value)
        return int(value)

    def serialize(self, value):
        value = super().serialize(value)
        return int(value)

    def validate(self, value):
        super().validate(value)
        if not isinstance(value, int):
            try:
                int(value)
            except ValueError:
                raise ValidationError(message='Not a valid integer')


class Raw(Field):
    pass


class Float(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def deserialize(self, value):
        value = super().deserialize(value)
        return float(value)

    def serialize(self, value):
        value = super().serialize(value)
        return float(value)

    def validate(self, value):
        super().validate(value)
        if not isinstance(value, float):
            try:
                float(value)
            except (ValueError, TypeError):
                raise ValidationError(message='Not a valid float')


class Datetime(Field):
    REGEXES = {
        'iso': re.compile(
            r"(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})"
            r"[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})"
            r"(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?"
            r"(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?$"
        )
    }

    @staticmethod
    def _get_fixed_timezone(offset):
        """Return a tzinfo instance with a fixed offset from UTC."""
        if isinstance(offset, datetime.timedelta):
            offset = offset.total_seconds() // 60
        sign = '-' if offset < 0 else '+'
        hhmm = '%02d%02d' % divmod(abs(offset), 60)
        name = sign + hhmm
        return datetime.timezone(datetime.timedelta(minutes=offset), name)

    def from_iso_format(self, value: datetime.datetime):
        """Parse a string and return a datetime.datetime.

        This function supports time zone offsets. When the input contains one,
        the output uses a timezone with a fixed offset from UTC.
        """
        match = self.REGEXES['iso'].match(value)
        kw = match.groupdict()
        kw['microsecond'] = (kw['microsecond']
                             and kw['microsecond'].ljust(6, '0'))
        tzinfo = kw.pop('tzinfo')
        if tzinfo == 'Z':
            tzinfo = datetime.timezone.utc
        elif tzinfo is not None:
            offset_mins = int(tzinfo[-2:]) if len(tzinfo) > 3 else 0
            offset = 60 * int(tzinfo[1:3]) + offset_mins
            if tzinfo[0] == "-":
                offset = -offset
            tzinfo = self._get_fixed_timezone(offset)
        kw = {k: int(v) for k, v in kw.items() if v is not None}
        kw['tzinfo'] = tzinfo
        return datetime.datetime(**kw)

    def to_iso_format(self, value: datetime.datetime):
        return value.isoformat()

    SERIALIZATION_FUNCS = {
        'iso': to_iso_format,
    }

    DESERIALIZATION_FUNCS = {
        'iso': from_iso_format,
    }

    DEFAULT_FORMAT = 'iso'

    def __init__(self, value_format=None, **kwargs):
        super().__init__(**kwargs)
        if not value_format:
            value_format = self.DEFAULT_FORMAT

        if (value_format not in self.DESERIALIZATION_FUNCS
                or value_format not in self.SERIALIZATION_FUNCS):
            raise InvalidParams(message=f'Unsupported format: {value_format}')

        self.value_format = value_format

    def validate(self, value):
        super().validate(value)

        if not isinstance(value, (str, datetime.datetime)):
            raise ValidationError(
                message='Invalid data. Only accept datetime str or object'
            )

        if isinstance(value, str):
            match = self.REGEXES[self.value_format].match(value)
            if not match:
                raise ValidationError(
                    message='Not a valid ISO8601-formatted datetime string'
                )

    def serialize(self, value):
        value = super().serialize(value)
        if isinstance(value, datetime.datetime):
            func = self.SERIALIZATION_FUNCS[self.value_format]
            value = func(self, value)
        return value

    def deserialize(self, value):
        value = super().deserialize(value)
        if isinstance(value, str):
            func = self.DESERIALIZATION_FUNCS[self.value_format]
            value = func(self, value)
        return value


class Dict(Field):
    def validate(self, value):
        super().validate(value)

        if not isinstance(value, dict):
            raise ValidationError('Not a valid dict')


class GeoPoint(Dict):
    def validate(self, value):
        super().validate(value)

        _type = value.get('type')
        if not _type:
            raise ValidationError(
                'Missing type'
            )
        if not isinstance(_type, str):
            raise ValidationError('type must be str')

        if _type != 'Point':
            raise ValidationError('type must be Point')

        coordinates = value.get('coordinates')
        if not coordinates:
            raise ValidationError('Missing coordinates')

        if not isinstance(coordinates, list):
            raise ValidationError('coordinates must be an array')

        try:
            long, lat = coordinates
        except ValueError:
            raise ValidationError(
                'Invalid coordinates. Must contains long, lat'
            )

        if not isinstance(long, (int, float)):
            raise ValidationError(
                'Invalid longitude. Must be an int and from -180 to 180'
            )
        if not isinstance(lat, (int, float)):
            raise ValidationError(
                'Invalid latitude. Must be an int and from -90 to 90'
            )


class GeoMultiPolygon(Dict):
    def validate(self, value):
        super().validate(value)

        _type = value.get('type')
        if not _type:
            raise ValidationError(
                'Missing type'
            )
        if not isinstance(_type, str):
            raise ValidationError('type must be str')

        if _type != 'MultiPolygon':
            raise ValidationError('type must be MultiPolygon')

        coordinates = value.get('coordinates')
        if not coordinates:
            raise ValidationError('Missing coordinates')

        if not isinstance(coordinates, list):
            raise ValidationError('coordinates must be an array')


class Nested(Field):
    def __init__(self, model, unknown=EXCLUDE, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.unknown = unknown

    def deserialize(self, value):
        value = super().deserialize(value)
        if isinstance(value, self.model):
            return value
        return self.model(**value)

    def serialize(self, value):
        value = super().serialize(value)
        if isinstance(value, self.model):
            return value.serialize()
        return value

    def validate(self, value):
        super().validate(value)

        if not isinstance(value, (dict, self.model)):
            raise ValidationError(
                message=f'Invalid data.'
                        f' Only accept dict or instance of {self.model}'
            )
        if isinstance(value, dict):
            value = self.model(**value)

        value.validate()


class List(Field):
    def __init__(self, item, **kwargs):
        super().__init__(**kwargs)
        if inspect.isclass(item):
            item = item()
        self.item = item

    def serialize(self, value):
        if isinstance(self.item, Nested):
            value = [self.item.serialize(v) for v in value]
        return value

    def deserialize(self, value):
        if isinstance(self.item, Nested):
            value = [self.item.deserialize(v) for v in value]
        return value

    def validate(self, value):
        if not isinstance(value, list):
            raise ValidationError(
                message='Not a valid list'
            )

        for v in value:
            self.item.validate(v)


class Phone(String):
    def _validate(self, value):
        super().validate(value)
        if not re.compile(PHONE_REGEX).match(value):
            raise ValidationError('Invalid phone format')


class File(Field):
    def validate(self, value):
        super().validate(value)
        if not isinstance(value, FileStorage):
            raise ValidationError('Not a valid file')


class Stream(Field):
    def validate(self, value):
        super().validate(value)
        if not isinstance(value, LimitedStream):
            raise ValidationError('Not a valid stream data')


class Range(List):
    def validate(self, value):
        super().validate(value)
        if len(value) != 2:
            raise ValidationError('Must contain only 2 items')


class TimeField(String):
    # TODO: add iso format and serialize, deserialize functions
    def validate(self, value):
        super().validate(value)
        if len(value) > 5:
            raise ValidationError('Invalid time.')
        try:
            hour, minute = value.split(':')
            hour = int(hour)
            minute = int(minute)
        except ValueError:
            raise ValidationError('Not a valid time format')

        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            raise ValidationError('Not a valid time value')
