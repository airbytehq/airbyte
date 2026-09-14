plugins {
    id("application")
    id("airbyte-bulk-connector")
    id("io.airbyte.gradle.docker")
    id("airbyte-connector-docker-convention")
}

airbyteBulkConnector {
    core = "load"
    toolkits = listOf("load-db")
}

application {
    mainClass = "io.airbyte.integrations.destination.dev_null_2.DevNull2DestinationKt"

    applicationDefaultJvmArgs = listOf(
        "-XX:+ExitOnOutOfMemoryError",
        "-XX:MaxRAMPercentage=75.0"
    )
}
