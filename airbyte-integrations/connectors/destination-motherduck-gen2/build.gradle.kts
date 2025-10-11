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
    mainClass = "io.airbyte.integrations.destination.motherduck.MotherDuckDestinationKt"
}

val hikariCpVersion = "7.0.2"
val junitVersion = "5.13.4"
val junitPlatformVersion = "1.13.4"
val duckdbJdbcVersion = "1.1.3"

dependencies {
    implementation("org.duckdb:duckdb_jdbc:$duckdbJdbcVersion")
    implementation("com.zaxxer:HikariCP:$hikariCpVersion")

    testImplementation("io.mockk:mockk:1.14.5")
    testImplementation("org.junit.jupiter:junit-jupiter-api:$junitVersion")
    testImplementation("org.junit.jupiter:junit-jupiter:$junitVersion")
    testRuntimeOnly("org.junit.platform:junit-platform-engine:$junitPlatformVersion")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher:$junitPlatformVersion")
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:$junitVersion")

    integrationTestImplementation("com.zaxxer:HikariCP:$hikariCpVersion")
    integrationTestImplementation("org.duckdb:duckdb_jdbc:$duckdbJdbcVersion")
    integrationTestImplementation(project(":airbyte-cdk:java:airbyte-cdk:airbyte-cdk-dependencies"))
}
