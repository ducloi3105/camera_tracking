from src.bases.models import MetaModel, BaseModel, fields
from src.common.utils import get_now, gen_uuid
from src.common.constants import STRING_LENGTH
from pymongo.collection import Collection


class DatabaseMetaModel(MetaModel):
    def __new__(mcs, name, bases, attrs):
        _indexes = dict()

        for parent_class in bases:
            parent_indexes = getattr(parent_class, '_indexes', dict())
            for key, value in parent_indexes.items():
                _indexes[key] = value

        for key, value in attrs.items():
            if key == '_indexes':
                if not isinstance(value, dict):
                    raise TypeError('_indexes must be a dict')

                for idx_key, idx_value in value.items():
                    _indexes[idx_key] = idx_value

        attrs['_indexes'] = _indexes

        return super().__new__(mcs, name, bases, attrs)


class Model(BaseModel, metaclass=DatabaseMetaModel):
    id = fields.String(default=gen_uuid,
                       max_length=STRING_LENGTH['SHORT'])

    created_at = fields.Datetime(default=get_now)
    updated_at = fields.Datetime()

    deleted = fields.Boolean(default=False)

    _translatable_fields: list = []

    _indexes = {
        'id': {}
    }

    @classmethod
    def get_collection_name(cls):
        return ''.join('_%s' % c if c.isupper() else c
                       for c in cls.__name__).strip('_').lower()

    @classmethod
    def list_indexes(cls):
        return cls._indexes

    def save(self, mongodb):
        self.validate()

        coll = mongodb[self.get_collection_name()]

        coll.update_one(
            {'id': self.id},
            {'$set': self.to_dict()},
            upsert=True
        )

        return self

    def to_dict(self, language_code: str = None, *args, **kwargs):
        result = super().to_dict(*args, **kwargs)

        if language_code and self._translatable_fields:
            translations = dict()
            for tf in self._translatable_fields:
                t_values = result.get(tf) or []
                try:
                    value = list(filter(
                        lambda x: x['language_code'] == language_code,
                        t_values
                    ))[0]
                    value = value['value']
                except IndexError:
                    value = t_values[0]['value']

                translations[tf] = value

            result.update(**translations)

        return result


class NestedModel(BaseModel):
    pass

