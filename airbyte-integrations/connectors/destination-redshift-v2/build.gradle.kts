plugins {
    id("application")
    id("airbyte-bulk-connector")
    id("io.airbyte.gradle.docker")
    id("airbyte-connector-docker-convention")
}

airbyteBulkConnector {
    core = "load"
    toolkits = listOf("load-csv", "load-aws")
}

tasks.withType<JavaCompile> {
    options.compilerArgs.add("-Xlint:-this-escape")
}

application {
    mainClass.set("io.airbyte.integrations.destination.redshift2.RedshiftDestinationKt")
    applicationDefaultJvmArgs = listOf(
        "-XX:+ExitOnOutOfMemoryError",
        "-XX:MaxRAMPercentage=75.0"
    )
}

val hikariCpVersion = "7.0.2"
val redshiftJdbcVersion = "2.1.0.30"
val awsSdkVersion = "1.12.780"
val testContainersVersion = "1.20.5"

dependencies {
    // Redshift JDBC driver
    implementation("com.amazon.redshift:redshift-jdbc42:$redshiftJdbcVersion")
    
    // Connection pooling
    implementation("com.zaxxer:HikariCP:$hikariCpVersion")
    
    // AWS S3 for staging (used by load-aws toolkit)
    implementation("com.amazonaws:aws-java-sdk-s3:$awsSdkVersion")
    
    // Utilities from old CDK (for JDBC URL parsing)
    implementation(project(":airbyte-cdk:java:airbyte-cdk:airbyte-cdk-core"))
    
    // Test dependencies
    testImplementation("io.mockk:mockk:1.14.5")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.10.2")
    
    // Integration test dependencies
    integrationTestImplementation("com.amazon.redshift:redshift-jdbc42:$redshiftJdbcVersion")
    integrationTestImplementation("org.testcontainers:postgresql:$testContainersVersion") // Redshift is Postgres-compatible
}
