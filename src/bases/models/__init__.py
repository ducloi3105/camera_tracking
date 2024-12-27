import json

from src.common import dict_utils
from src.common.json_encoders import CustomJsonEncoder

from . import fields
from . import errors


class MetaModel(type):
    def __new__(mcs, name, bases, attrs):
        _fields = dict()

        for parent_class in bases:
            parent_fields = getattr(parent_class, '_fields', dict())
            for key, value in parent_fields.items():
                _fields[key] = value

        for key, value in attrs.items():
            if key == '_indexes':
                if not isinstance(value, dict):
                    raise TypeError('_indexes must be a dict')

            if isinstance(value, fields.Field):
                _fields[key] = value

        for key in _fields:
            attrs[key] = None

        attrs['_fields'] = _fields

        return super().__new__(mcs, name, bases, attrs)


class BaseModel(metaclass=MetaModel):
    _fields: dict = dict()

    def __init__(self, **kwargs):
        self.load(kwargs)

    @staticmethod
    def _resolve_field_value_before_set(field, value: any):
        # For string array in str format
        if isinstance(field, fields.List) and isinstance(value, str):
            if value == '':
                value = []
            else:
                value = value.split(',')

        if isinstance(field, fields.Boolean) and isinstance(value, str):
            if value.lower() in ['true', 'false']:
                value = json.loads(value.lower())

        field.validate(value)

        return field.deserialize(value)

    def __setattr__(self, key, value):
        if key not in self._fields:
            raise AttributeError(
                f'{self.__class__} has not attribute {key}'
            )
        field = self._fields[key]
        if value is not None:
            value = self._resolve_field_value_before_set(field, value)
        return super().__setattr__(key, value)

    def validate(self):
        errs = {}
        for key, field in self._fields.items():

            value = getattr(self, key, None)

            if value is None:
                if field.required:
                    errs[key] = 'Field is required'
                    continue
                continue

            try:
                field.validate(value)
            except errors.ValidationError as e:
                errs[key] = e.output()

        if errs:
            raise errors.ValidationError(
                message='Invalid data',
                meta=errs
            )

    def load(self, data: dict):
        errs = {}
        for key, field in self._fields.items():
            if key not in data:
                continue
            try:
                setattr(self, key, data[key])
            except errors.ValidationError as e:
                errs[key] = e.output()

        if errs:
            raise errors.ValidationError(
                message='Invalid data',
                meta=errs
            )
        return self

    @classmethod
    def load_from_dict(cls, data: dict):

        result = cls()
        result.load(data)

        return result

    def serialize(self):

        data = dict()

        for key, field in self._fields.items():
            value = getattr(self, key, None)

            default_value = field.get_default()

            if value is None:
                value = default_value

            if value is not None:
                value = field.serialize(value)

            data[key] = value

        return data

    def _resolve_field_value_before_to_dict(self, value):
        if isinstance(value, list):
            return [self._resolve_field_value_before_to_dict(v) for v in value]

        if isinstance(value, BaseModel):
            return value.to_dict()

        return value

    def to_dict(self,
                include_keys: list = None,
                exclude_keys: list = None):

        data = dict()

        for key, field in self._fields.items():
            value = getattr(self, key, None)
            if value is None:
                value = field.get_default()
            else:
                value = self._resolve_field_value_before_to_dict(value)

            data[key] = value

        return dict_utils.filter_keys(
            data=data,
            include_keys=include_keys,
            exclude_keys=exclude_keys
        )

    def to_json(self,
                include_keys: list = None,
                exclude_keys: list = None):
        return json.dumps(
            dict_utils.filter_keys(
                data=self.serialize(),
                include_keys=include_keys,
                exclude_keys=exclude_keys
            ),
            cls=CustomJsonEncoder
        )

