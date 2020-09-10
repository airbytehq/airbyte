# Developing Locally

## Develop with Docker

```text
$ git clone git@github.com:datalineio/dataline.git
$ cd dataline
$ docker-compose -f docker-compose.dev.yaml up --build
```

The first build will take a few minutes, next ones will go faster. 

Once it completes, Dataline will be running in your environment.

## Develop with Gradle

Dataline uses `java 14` and `node 14`

To compile the code and run unit tests: 
```text
$ ./gradlew clean build
```

To run acceptance (end-to-end) tests: 
```
$ ./gradlew clean build :dataline-tests:acceptanceTests
```

> For this part we can be smart and leverage docker compose to start dependencies while the module we want to work on runs on the host system.

### Run the frontend separately

### Run the APIs separately

### Run the scheduler separately

## Code Style

‌For all the `java` code we follow Google's Open Sourced [style guide](https://google.github.io/styleguide/).‌

### Configure Java Style for IntelliJ <a id="configure-for-intellij"></a>

First download the style configuration

```text
$ curl https://github.com/google/styleguide/blob/gh-pages/intellij-java-google-style.xml -o ~/Downloads/intellij-java-google-style.xml
```

Install it in IntelliJ:‌

1. Go to `Preferences > Editor > Code Style`
2. Press the little cog:
   1. `Import Scheme > IntelliJ IDEA code style XML`
   2. Select the file we just downloaded
3. Select `GoogleStyle` in the drop down
4. You're done!

