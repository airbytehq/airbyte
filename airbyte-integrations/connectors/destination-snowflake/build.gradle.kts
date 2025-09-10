plugins {
    id("application")
    id("airbyte-bulk-connector")
    id("io.airbyte.gradle.docker")
    id("airbyte-connector-docker-convention")
}

airbyteBulkConnector {
    core = "load"
    toolkits = listOf("load-db")
    cdk = "local"
}

tasks.withType<JavaCompile>().configureEach {
    options.compilerArgs.add("-Xlint:-this-escape")
}

application {
    mainClass = "io.airbyte.integrations.destination.snowflake.SnowflakeDestinationKt"
// enable when profiling
    applicationDefaultJvmArgs = listOf(
            "-XX:+ExitOnOutOfMemoryError",
            "-XX:MaxRAMPercentage=75.0",
            "-XX:NativeMemoryTracking=detail",
            "-XX:+UnlockDiagnosticVMOptions",
            "-XX:GCLockerRetryAllocationCount=100",
//            "-XX:NativeMemoryTracking=detail",
//            "-Djava.rmi.server.hostname=localhost",
//            "-Dcom.sun.management.jmxremote=true",
//            "-Dcom.sun.management.jmxremote.port=6000",
//            "-Dcom.sun.management.jmxremote.rmi.port=6000",
//            "-Dcom.sun.management.jmxremote.local.only=false"
//            "-Dcom.sun.management.jmxremote.authenticate=false",
//            "-Dcom.sun.management.jmxremote.ssl=false",
    )
}

val junitVersion = "5.13.4"
val junitPlatformVersion = "1.13.4"

dependencies {
    implementation("net.snowflake:snowflake-jdbc-thin:3.26.1")
    implementation("net.snowflake:snowflake-ingest-sdk:4.3.0")
    implementation("com.zaxxer:HikariCP:7.0.2")

    testImplementation("io.mockk:mockk:1.14.5")
    testImplementation("org.junit.jupiter:junit-jupiter-api:$junitVersion")
    testImplementation("org.junit.jupiter:junit-jupiter:$junitVersion")
    testRuntimeOnly("org.junit.platform:junit-platform-engine:$junitPlatformVersion")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher:$junitPlatformVersion")
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:$junitVersion")
}
