#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import hashlib


def hash(value, hash_type="md5", salt=None):
    """
      Implementation of a custom Jinja2 hash filter
      Hash type defaults to 'md5' if one is not specified.

      If you are using this has function for GDPR compliance, then
      you should probably also pass in a salt as discussed in:
      https://security.stackexchange.com/questions/202022/hashing-email-addresses-for-gdpr-compliance

      This can be used in a low code connector definition under the AddFields transformation.
      For example:

    rates_stream:
      $ref: "*ref(definitions.base_stream)"
      $options:
        name: "rates"
        primary_key: "date"
        path: "/exchangerates_data/latest"
      transformations:
        - type: AddFields
          fields:
            - path: ["some_new_path"]
              value: "{{ record['rates']['CAD'] | hash('md5', 'mysalt')  }}"



      :param value: value to be hashed
      :param hash_type: valid hash type
      :param salt: a salt that will be combined with the value to ensure that the hash created for a given value on this system
                   is different from the hash created for that value on other systems.
      :return: computed hash as a hexadecimal string
    """
    hash_func = getattr(hashlib, hash_type, None)

    if hash_func:
        hash_obj = hash_func()
        hash_obj.update(str(value).encode("utf-8"))
        if salt:
            hash_obj.update(str(salt).encode("utf-8"))
        computed_hash = hash_obj.hexdigest()
    else:
        raise AttributeError("No hashing function named {hname}".format(hname=hash_type))

    return computed_hash


_filters_list = [hash]
filters = {f.__name__: f for f in _filters_list}
