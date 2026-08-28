/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

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
    mainClass.set("io.airbyte.integrations.destination.firebolt.FireboltDestinationKt")
    applicationDefaultJvmArgs = listOf(
        "-XX:+ExitOnOutOfMemoryError",
        "-XX:MaxRAMPercentage=75.0",
    )
}

val hikariCpVersion = "7.0.2"
val fireboltJdbcVersion = "3.3.0"
val awsSdkV2Version = "2.31.1"
val junitVersion = "5.13.4"
val junitPlatformVersion = "1.13.4"

dependencies {
    implementation("io.firebolt:firebolt-jdbc:$fireboltJdbcVersion")
    implementation("com.zaxxer:HikariCP:$hikariCpVersion")
    implementation("software.amazon.awssdk:s3:$awsSdkV2Version")
    implementation("de.siegmar:fastcsv:4.0.0")
    implementation(project(":airbyte-cdk:java:airbyte-cdk:airbyte-cdk-core"))

    testImplementation("io.mockk:mockk:1.14.5")
    testImplementation("org.junit.jupiter:junit-jupiter-api:$junitVersion")
    testImplementation("org.junit.jupiter:junit-jupiter:$junitVersion")
    testRuntimeOnly("org.junit.platform:junit-platform-engine:$junitPlatformVersion")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher:$junitPlatformVersion")
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:$junitVersion")
}
