When root is mentioned, it refers to this [folder](../..)
</br>
When module is mentioned, it refers to this [folder](.)

- The preferred language is kotlin
- kotlin is the only language that we need to use
- we are using gradle to build the module
- we are using git for version control
- The module is using the following frameworks
    - micronaut for dependency ingestion
    - mockk for mocking
    - we use the coroutine and the coroutine's flow for task execution
- the way to test if the module compiles is by running the gradle command `assemble`
- the way to run the test is by running the gradle command `test`
- the file [README.md](README.md) contains additional information
- When doing a modification to the module we need to:
    - update the file [build.gradle](build.gradle) where we need to bump the version. The version has a SemVer format and we need to increase the patch version
    - update the [changelog.md](changelog.md) where we need to add a description for the new version
    - If the version has already been bumped on the local branch, we shouldn't bump it again
- We format our code by running the command `pre-commit run --all-files` from the root of the project
- when writing a test function, the function name can't start with test because it is redundant

When you are done with a change always run the format and update the changelog if needed.