# Running Standard Source Tests for Python Integrations

## How to
(note: This is all going to be moved into the template as soon as our templating engine is merged. This is doc is written as if that template exists already. So it assumes that the basic file structure and templated files exist.)
In order to use the standard source tests, follow these steps:
* files for standard test
    * `standardtest/__init__.py`
    * `standardtest/standard_source_test.py`
    * `standardtestresources/`
    * `Dockerfile.test`
    * `requirements.standard-test.txt`
* In `standardtest/standard_source_test.py` implement the annotated methods. With information specific to your integration.
* Any files placed in the `secrets` and `standardtest` directory will be accessible in the test container / test class via `pkgutil`.
    * e.g. you can access them will the following Python: `pkgutil.get_data(self.__class__.__module__.split(".")[0], "spec.json")`
    * todo (cgardens) - we should standardize where `spec.json` goes, so that we can reliably pull that as well. Right now we look for it in the main module and pull it if we can find it. Maybe we should move it to a `resources` folder or something so that it is standardized.
* You can make modification to the test container in `Dockerfile.test`
* You can add any dependencies that the test code needs in `requirements.standard-test.txt` for local development and to the `standardtest` requirements in `setup.py` for when it runs in the docker container.
    * Note: by default, the test code does not depend on the main code.
