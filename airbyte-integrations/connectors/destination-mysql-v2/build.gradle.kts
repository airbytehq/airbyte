plugins {
    id("application")
    id("airbyte-bulk-connector")
    id("io.airbyte.gradle.docker")              // Docker build support
    id("airbyte-connector-docker-convention")   // Reads metadata.yaml
}

airbyteBulkConnector {
    core = "load"              // For destinations
    toolkits = listOf("load-db")  // Database toolkit
}

application {
    mainClass.set("io.airbyte.integrations.destination.mysql.MySQLDestinationKt")
    applicationDefaultJvmArgs = listOf("-XX:+ExitOnOutOfMemoryError", "-XX:MaxRAMPercentage=75.0")
}

dependencies {
    // MySQL JDBC driver
    implementation("com.mysql:mysql-connector-j:8.0.33")

    // HikariCP for connection pooling
    implementation("com.zaxxer:HikariCP:5.0.1")

    // Testcontainers for automated testing
    integrationTestImplementation("org.testcontainers:mysql:1.19.0")
}
