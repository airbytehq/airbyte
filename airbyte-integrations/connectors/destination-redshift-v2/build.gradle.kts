plugins {
    id("application")
    id("airbyte-bulk-connector")
    id("io.airbyte.gradle.docker")
    id("airbyte-connector-docker-convention")
}

airbyteBulkConnector {
    core = "load"
    toolkits = listOf("load-db", "load-s3")
}

application {
    mainClass = "io.airbyte.integrations.destination.redshift_v2.RedshiftV2DestinationKt"

    applicationDefaultJvmArgs = listOf(
        "-XX:+ExitOnOutOfMemoryError",
        "-XX:MaxRAMPercentage=75.0",
    )
}

val hikariCpVersion = "6.2.1"
val redshiftJdbcVersion = "2.1.0.31"

dependencies {
    implementation("com.amazon.redshift:redshift-jdbc42:$redshiftJdbcVersion")
    implementation("com.zaxxer:HikariCP:$hikariCpVersion")
}
