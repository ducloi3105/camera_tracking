from eventlet.greenpool import GreenPool

from src.common.dict_utils import flatten_dict


class Core(object):
    def __init__(self, mongodb, logger=None):
        self.logger = logger
        self.mongodb = mongodb

    @staticmethod
    def _sort(model, sorts):
        if not sorts:
            sorts = ['-created_at']

        sort_dict = {}

        for key in sorts:

            # get column name and descending
            if key.startswith('-'):
                field_name = key[1:len(key)]
                descending = True
            else:
                descending = False
                if key.startswith('+'):
                    field_name = key[1:len(key)]
                else:
                    field_name = key

            if descending:
                sort_dict[field_name] = -1
            else:
                sort_dict[field_name] = 1

        return sort_dict


class Crawler(Core):
    def __init__(self,
                 *,
                 bulk_size=None,
                 max_workers=None,
                 **kwargs, ):

        super().__init__(**kwargs)

        if not bulk_size:
            bulk_size = 500
        if not max_workers:
            max_workers = 10
        self.bulk_size = bulk_size
        self.max_workers = max_workers

        self.worker_pool = GreenPool(self.max_workers)

    @staticmethod
    def _prepare_update_payload(obj,
                                exclude_keys=None):
        if not exclude_keys:
            exclude_keys = []

        translatable_fields = getattr(obj, '_translatable_fields', [])

        translations = {}
        object_data = obj.to_dict()
        for tk in translatable_fields:
            tl_value = object_data.pop(tk, None)
            if not tl_value:
                continue
            translations[tk] = tl_value

        for ek in exclude_keys:
            object_data.pop(ek, None)

        update_data = {}

        for k, v in flatten_dict(object_data).items():
            if not v:
                continue
            update_data[k] = v

        result = [
            {
                '$set': flatten_dict(update_data)
            }
        ]

        if translations:
            for key, trans in translations.items():
                for tran in trans:
                    result.append({
                        '$set': {
                            key: {
                                '$concatArrays': [
                                    [tran],
                                    {
                                        '$ifNull': [
                                            {'$filter': {
                                                'input': f'${key}',
                                                'as': key,
                                                'cond': {
                                                    '$ne': [
                                                        f'$${key}.language_code',
                                                        tran['language_code']
                                                    ]
                                                }
                                            }},
                                            []
                                        ]
                                    }
                                ]
                            }
                        }
                    })

        return result

    def _bulk_write(self, ops):
        mapped_ops = {}
        for op in ops:
            model = op['model']
            coll_name = model.get_collection_name()
            if coll_name not in mapped_ops:
                mapped_ops[coll_name] = {
                    'model': model,
                    'ops': []
                }
            mapped_ops[coll_name]['ops'].append(op['operation'])

        worker_pool = GreenPool(self.max_workers)

        for coll_name, coll_data in mapped_ops.items():
            coll = self.mongodb[coll_name]
            worker_pool.spawn(
                coll.bulk_write,
                coll_data['ops']
            )
        worker_pool.waitall()
        print(f'_bulk_write {len(ops)} records')

    def _wait_for_workers(self):
        self.worker_pool.waitall()

    def run(self):
        raise NotImplementedError
