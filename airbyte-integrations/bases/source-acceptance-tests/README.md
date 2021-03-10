# Source Acceptance Tests

## Overview

Testing is an important part of building a reliable connector, but it can be tedious to think of and implement good test cases. This library reduces the burden of testing by providing various test banks that verify connectors behave as advertised. This library works with connectors written in any language and can be configured completely through a YAML file.   

### What this library does
1. Provide a low overhead way to test basic functionality for any Airbyte source. 
1. Require minimum effort from the author of the integration.

### What this library _does not_ do 
1. Test corner cases for specific integrations.
1. Replace good unit testing and thorough integration testing for the integration.

In order to guarantee a baseline of quality for its users, Airbyte will _not_ merge sources that cannot pass these tests unless the author can provide a very good reason™.

## What's provided by this library?
This library is structured as follows: 
1. **Test Banks**: Each test bank verifies that a particular category of connector behaves correctly. We currently provide the following banks: 
    1. **Core**: Tests basic functionality that every Airbyte source must fulfill
    1. **Full Refresh**: Any source which supports full refresh syncs on any of its streams should pass this test suite
    1. **Incremental**: Any source which supports incremental syncs on any of its streams should pass this test suite 
1. **Test Runner**: This is the entry point which invokes the library. Currently, the test runner accepts a YAML configuration which declares which test suites should run and provides the appropriate inputs to them


## Cool. I'm in. How can I get started?

### TL;DR 
1. Configure your tests via `acceptance_tests.yaml`
2. Create files needed for tests (e.g: Configured Catalog, connector configuration, etc..)
3. Invoke the test library via Docker, mounting both your `acceptance_tests.yaml` and any files needed for the tests (the ones you created in step 2) into the Docker image

### In more details
If you generated your source using one of Airbyte's template generators, you should already have a YAML file in your connector module root called `acceptance_tests.yaml`. If not, create one.

`acceptance_tests.yml` should adhere to the schema described by this [YAML file](src/main/resources/schemas/source_acceptance_test_inputs.yaml). See the linked YAML schema for a description of what each field means.

Once the YAML configuration is ready, from your connector module root simply run `docker run -v $(pwd):/test_inputs/ -w /test_inputs/ airbyte/source-acceptance-tests`. This will mount your entire connector module directory into the test runner's filesystem, thereby making available any files you referenced in `acceptance_tests.yaml`. 

That's it. That's the whole thing. 

If your tests fail, follow the information provided by the test output to identify the problems. 

### FAQ
**I wrote my connector in language X. Can I use this test suite?**

Yes! As long as your connector is packaged in a Docker container, this library can test it. 

**I need to spin up and tear down resources before/after my tests. How can I do this if this library only accepts YAML?**

We recommend: 
1. Packaging your test resources in a Docker image that you build before invoking this test library and then
2. In a bash script, spin up the Docker image, invoke this library, then tear down your resources after running the tests

Alternatively if your connector is written in a JVM language like Java, you can extend the test banks directly (they're just Junit Test cases) and override the `@BeforeEach`/`@BeforeAll` etc.. methods. Go wild.  
