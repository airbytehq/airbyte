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

tasks.withType<JavaCompile> {
    options.compilerArgs.add("-Xlint:-this-escape")
}

application {
    mainClass.set("io.airbyte.integrations.destination.redshift.RedshiftDestinationKt")
    applicationDefaultJvmArgs = listOf(
        "-XX:+ExitOnOutOfMemoryError",
        "-XX:MaxRAMPercentage=75.0"
    )
}

val hikariCpVersion = "7.0.2"
val redshiftJdbcVersion = "2.2.7"
val awsSdkV2Version = "2.31.1"
val junitVersion = "5.13.4"
val junitPlatformVersion = "1.13.4"

dependencies {
    // Redshift JDBC driver
    implementation("com.amazon.redshift:redshift-jdbc42:$redshiftJdbcVersion")

    // High-performance CSV writer for staging files
    implementation("de.siegmar:fastcsv:4.0.0")
    
    // Connection pooling
    implementation("com.zaxxer:HikariCP:$hikariCpVersion")
    
    // AWS S3 for staging (SDK v2)
    implementation("software.amazon.awssdk:s3:$awsSdkV2Version")
    
    // SSH tunnel support (from old CDK)
    implementation(project(":airbyte-cdk:java:airbyte-cdk:airbyte-cdk-core"))
    
    // Test dependencies
    testImplementation("io.mockk:mockk:1.14.5")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.10.2")
    
    // JUnit version alignment (required for Gradle 8.14+)
    testImplementation("org.junit.jupiter:junit-jupiter-api:$junitVersion")
    testImplementation("org.junit.jupiter:junit-jupiter:$junitVersion")
    testRuntimeOnly("org.junit.platform:junit-platform-engine:$junitPlatformVersion")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher:$junitPlatformVersion")
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:$junitVersion")
}
