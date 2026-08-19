plugins {
    id("application")
    id("airbyte-bulk-connector")
    id("io.airbyte.gradle.docker")
    id("airbyte-connector-docker-convention")
}

airbyteBulkConnector {
    core = "load"
    toolkits = listOf("load-csv")
}

application {
    mainClass = "io.airbyte.integrations.destination.redshift_v2.RedshiftV2DestinationKt"

    applicationDefaultJvmArgs = listOf(
        "-XX:+ExitOnOutOfMemoryError",
        "-XX:MaxRAMPercentage=75.0",
    )
}

val hikariCpVersion = "7.0.2"
val redshiftJdbcVersion = "2.1.0.31"

dependencies {
    implementation("com.amazon.redshift:redshift-jdbc42:$redshiftJdbcVersion")
    implementation("com.zaxxer:HikariCP:$hikariCpVersion")

    implementation("software.amazon.awssdk:s3:2.27.21")
    implementation("software.amazon.awssdk.crt:aws-crt:0.30.11")
    implementation("de.siegmar:fastcsv:4.0.0")
}
