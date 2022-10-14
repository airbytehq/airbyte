import hashlib

def hash(value, hash_type="md5", salt=None):
    """
    Example filter providing custom Jinja2 filter - hash

    Hash type defaults to 'sha1' if one is not specified

    :param value: value to be hashed
    :param hash_type: valid hash type
    :return: computed hash as a hexadecimal string
    """
    hash_obj = getattr(hashlib, hash_type, None)()
    hash_obj.update(str(value).encode("utf-8"))
    hash_obj.update(str(salt).encode("utf-8"))


    if hash_obj:
        computed_hash = hash_obj.hexdigest()
    else:
        raise AttributeError(
            "No hashing function named {hname}".format(hname=hash_type)
        )

    return computed_hash


_filters_list = [hash]
filters = {f.__name__: f for f in _filters_list}
