# Updating Gradle Dependencies
We use [Gradle Catalogs](https://docs.gradle.org/current/userguide/platforms.html#sub:central-declaration-of-dependencies)
to keep dependencies synced up across different Java projects. This is particularly useful for Airbyte Cloud, and can be
used by any project seeking to build off Airbyte.

Catalogs allow dependencies to be represented as dependency coordinates. A user can reference preset dependencies/versions
when declaring dependencies in a build script.

> Version Catalog Example:
> ```gradle
> dependencies {
>    implementation(libs.groovy.core)
> }
> ```
> In this context, libs is a catalog and groovy represents a dependency available in this catalog. Instead of declaring a
> specific version, we reference the version in the Catalog.

This helps reduce the chances of dependency drift and dependency hell.

Thus, please use the Catalog when:
- declaring new common dependencies.
- specifying new common dependencies.

A common dependency is a foundational Java package e.g. Apache commons, Log4j etc that is often the basis on which libraries
are built upon.

This is a relatively new addition, so devs should keep this in mind and use the top-level Catalog on a best-effort basis.

### Setup Details
This section is for engineers wanting to understand Gradle Catalog details and how Airbyte has set this up.

#### The version catalog TOML file format
Gradle offers a conventional file to declare a catalog.
It’s a conventional location to declare dependencies that are both consumed and published.

The TOML file consists of 4 major sections:
- the [versions] section is used to declare versions which can be referenced by dependencies
- the [libraries] section is used to declare the aliases to coordinates
- the [bundles] section is used to declare dependency bundles
- the [plugins] section is used to declare plugins

> TOML file Example:
> ```gradle
> [versions]
> groovy = "3.0.5"
>
> [libraries]
> groovy-core = { module = "org.codehaus.groovy:groovy", version.ref = "groovy" }
>
> [bundles]
> groovy = ["groovy-core", "groovy-json", "groovy-nio"]
>
> [plugins]
> jmh = { id = "me.champeau.jmh", version = "0.6.5" }
> ```
> NOTE: for more information please follow [this](https://docs.gradle.org/current/userguide/platforms.html#:~:text=The%20version%20catalog%20TOML%20file%20format
) link.

As described above this project contains TOML file `deps.toml` which is fully fulfilled with respect to [official](https://docs.gradle.org/current/userguide/platforms.html#sub::toml-dependencies-format) documentation.
In case when new versions should be used please update `deps.toml` accordingly.

<details>
<summary>deps.toml</summary>

[versions]
fasterxml_version = "2.13.0"
glassfish_version = "2.31"
commons_io = "2.7"
log4j = "2.17.1"
slf4j = "1.7.30"
lombok = "1.18.22"
junit-jupiter = "5.8.2"

[libraries]
fasterxml = { module = "com.fasterxml.jackson:jackson-bom", version.ref = "fasterxml_version" }
glassfish = { module = "org.glassfish.jersey:jackson-bom", version.ref = "glassfish_version" }
jackson-databind = { module = "com.fasterxml.jackson.core:jackson-databind", version.ref = "fasterxml_version" }
jackson-annotations = { module = "com.fasterxml.jackson.core:jackson-annotations", version.ref = "fasterxml_version" }
jackson-dataformat = { module = "com.fasterxml.jackson.dataformat:jackson-dataformat-yaml", version.ref = "fasterxml_version" }
jackson-datatype = { module = "com.fasterxml.jackson.datatype:jackson-datatype-jsr310", version.ref = "fasterxml_version" }
guava = { module = "com.google.guava:guava", version = "30.1.1-jre" }
commons-io = { module = "commons-io:commons-io", version.ref = "commons_io" }
apache-commons = { module = "org.apache.commons:commons-compress", version = "1.20" }
apache-commons-lang = { module = "org.apache.commons:commons-lang3", version = "3.11" }
slf4j-api = { module = "org.slf4j:slf4j-api", version = "1.7.30" }
log4j-api = { module = "org.apache.logging.log4j:log4j-api", version.ref = "log4j" }
log4j-core = { module = "org.apache.logging.log4j:log4j-core", version.ref = "log4j" }
log4j-impl = { module = "org.apache.logging.log4j:log4j-slf4j-impl", version.ref = "log4j" }
log4j-web = { module = "org.apache.logging.log4j:log4j-web", version.ref = "log4j" }
jul-to-slf4j = { module = "org.slf4j:jul-to-slf4j", version.ref = "slf4j" }
jcl-over-slf4j = { module = "org.slf4j:jcl-over-slf4j", version.ref = "slf4j" }
log4j-over-slf4j = { module = "org.slf4j:log4j-over-slf4j", version.ref = "slf4j" }
appender-log4j2 = { module = "com.therealvan:appender-log4j2", version = "3.6.0" }
aws-java-sdk-s3 = { module = "com.amazonaws:aws-java-sdk-s3", version = "1.12.6" }
google-cloud-storage = { module = "com.google.cloud:google-cloud-storage", version = "2.2.2" }
s3 = { module = "software.amazon.awssdk:s3", version = "2.16.84" }
lombok = { module = "org.projectlombok:lombok", version.ref = "lombok" }
junit-jupiter-engine = { module = "org.junit.jupiter:junit-jupiter-engine", version.ref = "junit-jupiter" }
junit-jupiter-api = { module = "org.junit.jupiter:junit-jupiter-api", version.ref = "junit-jupiter" }
junit-jupiter-params = { module = "org.junit.jupiter:junit-jupiter-params", version.ref = "junit-jupiter" }
mockito-junit-jupiter = { module = "org.mockito:mockito-junit-jupiter", version = "4.0.0" }
assertj-core = { module = "org.assertj:assertj-core", version = "3.21.0" }
junit-pioneer = { module = "org.junit-pioneer:junit-pioneer", version = "1.6.2" }
findsecbugs-plugin = { module = "com.h3xstream.findsecbugs:findsecbugs-plugin", version = "1.11.0" }

[bundles]
jackson = ["jackson-databind", "jackson-annotations", "jackson-dataformat", "jackson-datatype"]
apache = ["apache-commons", "apache-commons-lang"]
log4j = ["log4j-api", "log4j-core", "log4j-impl", "log4j-web"]
slf4j = ["jul-to-slf4j", "jcl-over-slf4j", "log4j-over-slf4j"]
junit = ["junit-jupiter-api", "junit-jupiter-params", "mockito-junit-jupiter"]

</details>

#### Declaring a version catalog
Version catalogs can be declared in the settings.gradle file.
There should be specified section `dependencyResolutionManagement` which uses `deps.toml` file as a declared catalog.
> Example:
> ```gradle
> dependencyResolutionManagement {
>     repositories {
>         maven {
>             url 'https://airbyte.mycloudrepo.io/public/repositories/airbyte-public-jars/'
>        }
>     }
>     versionCatalogs {
>         libs {
>             from(files("deps.toml"))
>         }
>     }
> }
> ```

#### Sharing Catalogs
To share this catalog for further usage by other Projects, we do the following 2 steps:
- Define `version-catalog` plugin in `build.gradle` file (ignore if this record exists)
  ```gradle
  plugins {
      id '...'
      id 'version-catalog'
  ```
- Prepare Catalog for Publishing
  ```gradle
  catalog {
      versionCatalog {
          from(files("deps.toml")) < --- declere either dependencies or specify existing TOML file
      }
  }
  ```

#### Configure the Plugin Publishing Plugin
To **Publishing**, first define the `maven-publish` plugin in `build.gradle` file (ignore if this already exists):
```gradle
plugins {
    id '...'
    id 'maven-publish'
}
```
After that, describe the publishing section. Please use [this](https://docs.gradle.org/current/userguide/publishing_gradle_plugins.html) official documentation for more details.
> Example:
> ```gradle
> publishing {
>     publications {
>         maven(MavenPublication) {
>             groupId = 'io.airbyte'
>             artifactId = 'oss-catalog'
>
>                 from components.versionCatalog
>         }
>     }
>
>     repositories {
>         maven {
>             url 'https://airbyte.mycloudrepo.io/repositories/airbyte-public-jars'
>             credentials {
>                 name 'cloudrepo'
>                 username System.getenv('CLOUDREPO_USER')
>                 password System.getenv('CLOUDREPO_PASSWORD')
>             }
>         }
>
>         mavenLocal()
>     }
> }
> ```
