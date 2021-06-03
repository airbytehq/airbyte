# Gradle Cheatsheet

## Python connector development
The ideal end state for a Python connector developer is that they shouldn't have to know Gradle exists. 

We're almost there, but today there is only one Gradle command that's needed when developing in Python, used for formatting code.

**Formatting python module**: `./gradlew :airbyte-integrations:connectors:<name>:airbytePythonFormat:

