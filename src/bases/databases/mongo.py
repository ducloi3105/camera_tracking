from pymongo import MongoClient, errors, database, TEXT, ASCENDING

from .models import Model


class Query(object):
    def __init__(self,
                 mongodb,
                 model,
                 fields=None,
                 sorts=None,
                 filters=None,
                 limit=None,
                 offset=None):
        self.mongodb = mongodb
        self.model = model

        if not filters:
            filters = {}
        if not fields:
            fields = []
        if not sorts:
            sorts = []

        self.fields = fields
        self.sorts = sorts
        self.filters = filters
        self.limit = limit
        self.offset = offset

        self._cursor = 0
        self._query = self._init_query()

    def _init_query(self):
        filters = self.filters
        result = self.mongodb[self.model.get_collection_name()].find(filters)
        if self.sorts:
            result = result.sort(self.sorts)

        if self.limit:
            result = result.limit(self.limit)

        if self.offset is not None:
            result = result.skip(self.offset)

        return result

    def filter(self, filters, **options):
        for k, v in filters.items():
            self.filters[k] = v
        return self

    def first(self):
        self._query = self._init_query()
        try:
            record = self._query[0]
        except IndexError:
            return None
        return self.model(**record)

    def get(self, id):
        record = self.mongodb[self.model.get_collection_name()].find_one({
            'id': id
        })
        if not record:
            return None

        return self.model(**record)

    def paginate(self, page, per_page):
        self.limit = per_page
        self.offset = (page - 1) * per_page
        return self

    def sort(self, *sorts):
        for s in sorts:
            self.sorts.append(s)
        return self

    def __iter__(self):
        self._query = self._init_query()
        self._cursor = 0
        return self

    def __next__(self):

        if self.limit:
            if self._cursor >= self.limit:
                raise StopIteration

        try:
            record = self._query[self._cursor]
        except IndexError:
            raise StopIteration

        self._cursor += 1

        return self.model(**record)


class Database(database.Database):
    query_class = Query

    def drop_indexes(self):
        for coll_name in self.list_collection_names():
            coll = self[coll_name]
            coll.drop_indexes()

    def create_indexes(self, models):
        for model in models:
            indexes = model.list_indexes()
            for index_name, index_data in indexes.items():

                index_payload = dict(
                    keys=[],
                    name=index_name
                )

                fields = index_data.get('fields', [index_name])
                index_type = index_data.get('type', ASCENDING)
                if index_type == TEXT:
                    weights = index_data.get('weights')
                    if weights:
                        index_payload['weights'] = weights

                for field in fields:
                    index_payload['keys'].append((field, index_type))

                coll_name = model.get_collection_name()
                coll = self[coll_name]

                try:
                    coll.create_index(**index_payload)
                except errors.OperationFailure:
                    coll.drop_index(index_name)
                    coll.create_index(**index_payload)

    def query(self, model: Model, *fields) -> Query:
        return self.query_class(
            mongodb=self,
            model=model,
            fields=fields
        )


class Mongo(MongoClient):
    def get_database(
            self,
            name=None,
            codec_options=None,
            read_preference=None,
            write_concern=None,
            read_concern=None,
    ):
        if name is None:
            name = 'storage'

        return Database(
            self, name,
            codec_options,
            read_preference,
            write_concern,
            read_concern
        )


