# Standard Source Test

## Overview

### These tests are designed to do the following:
1. Test basic functionality for any Airbyte source. Think of it as an "It works!" test.
    1. Each test should test functionality that is expected of all Airbyte sources.
1. Require minimum effort from the author of the integration.
    1. Think of these are "free" tests that Airbyte provides to make sure the integration works.
1. To be run for ALL Airbyte sources.

### These tests are _not_ designed to do the following:
1. Test any integration-specific cases.
1. Test corner cases for specific integrations.
1. Replace good unit testing and integration testing for the integration.

We will _not_ merge sources that cannot pass these tests unless the author can provide a very good reason™.

## What tests do the standard tests include?
Check out each function in [SourceAcceptanceTest](src/main/java/io/airbyte/integrations/standardtest/source/SourceAcceptanceTest.java). Each function annotated with `@Test` is a single test. Each of these functions is proceeded by comments that document what they are testing.

## How to run them from your integration?
* If writing a source in Python, check out this [readme](../base-python-test/readme.md)

## What do I need to provide as input to these tests?
* The name of the image of your integration (with the `:dev` tag at the end).
* A handful of json inputs, e.g. a valid configuration file and a catalog that will be used to try to run the `read` operation on your integration. These are fully documented in [SourceAcceptanceTest](src/main/java/io/airbyte/integrations/standardtest/source/SourceAcceptanceTest.java). Each method that is marked as `abstract` are methods that the user needs to implement to provide the necessary information. Each of these methods are preceded by comments explaining what they need to return.
* Optionally you can run before and after methods before each test.

## Do I have to write java to use these tests?
No! Our goal is to allow you to write your integration _entirely_ in your language of choice. If you are writing an integration in Python, for instance, you should be able to interact with this test suite in python and not need to write java. _Right now, we only have a Python interface to reduce friction for interacting with these tests_, and with time, we intend to make more language-specific helpers available. In the meantime, however, you can still use your language of choice and leverage this standard test suite. 

If working in Python, the Python interface that you need to implement can be found [here](../base-python-test/base_python_test/test_iface.py). Our [python template](../../connector-templates/source-python/README.md.hbs) and [singer template](../../connector-templates/source-singer/README.md.hbs) also walk you through how to implement the interface.
