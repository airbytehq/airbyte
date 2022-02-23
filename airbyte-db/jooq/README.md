# jOOQ Code Generation

## How to Use
This module generates jOOQ code for the configs and jobs database. To use the generated code, add the following dependency:

```gradle
dependencies {
  implementation project(':airbyte-db:jooq')
}
```

The generated code exists in the package `io.airbyte.db.instance.<db-name>.jooq` under the directory `build/generated/<db-name>Database/src/main/java`.

## Code Generation
Gradle plugin `nu.studer.jooq` is used for jOOQ code generation. See [here](https://github.com/etiennestuder/gradle-jooq-plugin) for details.

It is necessary to separate this module from the `lib` module, because we use a custom database (`FlywayMigrationDatabase`) that runs Flyway migration first for the code generator. This implementation needs to be compiled before it can be used.

The code will be automatically generated when this module is compiled. To manually update the generated code, run the `compileJava` task:

```sh
SUB_BUILD=PLATFORM ./gradlew :airbyte-db:jooq:compileJava
```

Or run the following tasks for individual database:

```sh
# for configs database
SUB_BUILD=PLATFORM ./gradlew :airbyte-db:jooq:generateConfigsDatabaseJooq

# for jobs database
SUB_BUILD=PLATFORM ./gradlew :airbyte-db:jooq:generateJobsDatabaseJooq
```

## How to Setup Code Generation for New Database
- In `build.gradle`, do the following.
- Add a new jOOQ configuration under `jooq.configuration`.
  - This step will automatically create a `generate<db-name>DatabaseJooq` task.
- Register the output of the code generation task in the main sourceSet.
- Setup caching for the code generation task.

Template:

```build.gradle
// add jooq configuration
jooq {
  configurations {
    <db-name>Database {
      generateSchemaSourceOnCompilation = true
      generationTool {
        generator {
          name = 'org.jooq.codegen.DefaultGenerator'
          database {
            name = 'io.airbyte.db.instance.configs.ConfigsFlywayMigrationDatabase'
            inputSchema = 'public'
            excludes = 'airbyte_configs_migrations'
          }
          target {
            packageName = 'io.airbyte.db.instance.configs.jooq'
            directory = 'build/generated/configsDatabase/src/main/java'
          }
        }
      }
    }
  }
}

// register output as source set
sourceSets.main.java.srcDirs (
  tasks.named('generate<db-name>DatabaseJooq').flatMap { it.outputDir }
)

sourceSets {
  main {
    java {
      srcDirs "$buildDir/generated/<db-name>Database/src/main/java"
    }
  }
}

// setup caching
tasks.named('generate<db-name>DatabaseJooq').configure {
  allInputsDeclared = true
  outputs.cacheIf { true }
}
```
