from __future__ import unicode_literals

import json
import sys
import sysconfig
import warnings

dest_prefix = sys.argv[1]
with warnings.catch_warnings():  # disable warning for PEP-632
    warnings.simplefilter("ignore")
    try:
        import distutils.sysconfig

        data = distutils.sysconfig.get_python_lib(prefix=dest_prefix)
    except ImportError:  # if removed or not installed ignore
        config_vars = {
            k: dest_prefix if any(v == p for p in (sys.prefix, sys.base_prefix)) else v
            for k, v in sysconfig.get_config_vars().items()
        }
        data = sysconfig.get_path("purelib", vars=config_vars)

print(json.dumps({"dir": data}))
