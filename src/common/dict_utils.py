def get_diff_keys(from_keys, to_keys):
    result = []

    check_fields = list(map(
        lambda f: '.'.join(f),
        to_keys
    ))
    for array_type_field in from_keys:
        is_ok = True

        str_type_field = '.'.join(array_type_field)
        for cf in check_fields:
            if str_type_field.startswith(cf):
                is_ok = False
                break

        if not is_ok:
            continue

        result.append(array_type_field)

    return result


def dive_to_get_value(data, path, default=None):
    key = path[0]
    value = data.get(key)

    if not value:
        return default

    if len(path) == 1:
        return value

    if not isinstance(value, dict):
        raise TypeError('Can only dive to dict')

    return dive_to_get_value(value, path[1:], default)


def dive_to_set_value(data, path, value=None):
    key = path[0]

    if len(path) == 1:
        data[key] = value
        return

    if key not in data:
        data[key] = {}

    return dive_to_set_value(data[key], path[1:], value)


def copy_value_by_path(origin,
                       path,
                       result,
                       current_level=None):
    if not path:
        return result

    if not current_level:
        current_level = []

    key = path[0]
    if key not in origin:
        return result

    value = origin.get(key)
    current_level.append(key)

    if not value or len(path) == 1:
        dive_to_set_value(result, current_level, value)
        return result

    if isinstance(value, list):
        current_data = dive_to_get_value(result, current_level, [])
        path = path[1:]

        for index, i in enumerate(value):
            if isinstance(i, list):
                raise ValueError(
                    'Unsupported list nested inside list at key: %s' % key)

            try:
                v = current_data[index]
            except IndexError:
                v = None

            if not isinstance(i, dict):
                try:
                    current_data[index] = i
                except IndexError:
                    current_data.append(i)
                continue

            if not v:
                v = {}
                current_data.append(copy_value_by_path(i, path, v))
            else:
                current_data[index] = copy_value_by_path(i, path, v)

        dive_to_set_value(result, current_level, current_data)

    return copy_value_by_path(value, path[1:], result, current_level)


def flatten_keys(data, pre=None):
    pre = pre[:] if pre else []
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                for d in flatten_keys(value, pre + [key]):
                    yield d
            # elif isinstance(value, (list, tuple, set)):
            #     if not len(value):
            #         continue
            #     v = value[0]
            #     for d in flatten_keys(v, pre + [key]):
            #         yield d
            else:
                yield pre + [key]
    else:
        yield pre


def filter_keys(data: dict,
                include_keys: list = None,
                exclude_keys: list = None):
    if not include_keys:
        include_keys = []
    if not exclude_keys:
        exclude_keys = []

    if not include_keys and not exclude_keys:
        return data

    result = dict()

    ild_keys = list(map(
        lambda f: f.split(','),
        include_keys
    ))

    eld_keys = list(map(
        lambda f: f.split(','),
        exclude_keys
    ))

    if ild_keys:
        result_keys = ild_keys
    else:
        result_keys = list(flatten_keys(data))
        result_keys = get_diff_keys(
            result_keys,
            eld_keys
        )

    for k in result_keys:
        result = copy_value_by_path(data, k, result)
    return result


def get_diff(origin: dict, collation: dict):

    # for now we can only check changes on FLATTENED dicts
    _origin = {}
    for k, v in origin.items():
        if isinstance(v, (list, dict)):
            continue
        _origin[k] = v

    _collation = {}
    for k, v in collation.items():
        if isinstance(v, (list, dict)):
            continue
        _collation[k] = v

    result = dict(
        set(_collation.items()) - set(_origin.items())
    )
    return result


def flatten_dict(data):
    return dict(
        ('.'.join(k), dive_to_get_value(data=data, path=k))
        for k in flatten_keys(data=data)
    )
