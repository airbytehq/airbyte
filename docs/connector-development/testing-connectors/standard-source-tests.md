# Standard Source Test Suite

## Sources written by Python

2 types of tests should be distinguished:
1. UnitTests [wiki](https://en.wikipedia.org/wiki/Unit_testing)
2. IntegrationTests [wiki](https://en.wikipedia.org/wiki/Integration_testing)


They have to be allocated into the following folders for corrected working of them with Airbyte CI/CD workflows:
1. unit_tests
2. integration_tests 

### Unit Tests
Launch methods:
1. by pytest directly: 
```
python -m pytest unit_tests
```
2. by gradle utility:
```
./gradlew --no-daemon :airbyte-integrations:connectors:<source_folder>:unitTest
```

### Integration Tests

Launch methods:
1. by pytest directly: 
```
python -m pytest integration_tests
```
2. by gradle utility:
```
./gradlew --no-daemon :airbyte-integrations:connectors:<source_folder>:integrationTest
```
*Note*: All gradle commands should be run from Airbyte project root only.


