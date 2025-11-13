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

tasks.withType<JavaCompile>().configureEach {
    options.compilerArgs.add("-Xlint:-this-escape")
}

application {
    mainClass = "io.airbyte.integrations.destination.mysql_v2.MysqlDestinationKt"
    applicationDefaultJvmArgs = listOf(
        "-XX:+ExitOnOutOfMemoryError",
        "-XX:MaxRAMPercentage=75.0",
        "-XX:NativeMemoryTracking=detail",
        "-XX:+UnlockDiagnosticVMOptions",
        "-XX:GCLockerRetryAllocationCount=100",
    )
}

val hikariCpVersion = "5.1.0"
val mysqlConnectorVersion = "9.1.0"
val junitVersion = "5.10.2"
val junitPlatformVersion = "1.10.2"
val testcontainersVersion = "1.19.3"

dependencies {
    // MySQL JDBC Driver
    implementation("com.mysql:mysql-connector-j:$mysqlConnectorVersion")

    // Connection Pooling
    implementation("com.zaxxer:HikariCP:$hikariCpVersion")

    // Testing
    testImplementation("io.mockk:mockk:1.13.10")
    testImplementation("org.junit.jupiter:junit-jupiter-api:$junitVersion")
    testImplementation("org.junit.jupiter:junit-jupiter:$junitVersion")
    testRuntimeOnly("org.junit.platform:junit-platform-engine:$junitPlatformVersion")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher:$junitPlatformVersion")
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:$junitVersion")

    // Integration Tests
    integrationTestImplementation(project(":airbyte-cdk:java:airbyte-cdk:airbyte-cdk-dependencies"))

    // Testcontainers for integration testing
    integrationTestImplementation("org.testcontainers:mysql:$testcontainersVersion")
    integrationTestImplementation("org.testcontainers:testcontainers:$testcontainersVersion")
    integrationTestImplementation("org.testcontainers:junit-jupiter:$testcontainersVersion")
}
