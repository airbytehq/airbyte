plugins {
    id("com.google.protobuf") version("0.9.4")
}

kotlin {
    sourceSets {
        // grab the “main” sourceSet
        val main by getting {
            // add each generated folder
            kotlin.srcDir(layout.buildDirectory.dir("generated/source/proto/main/grpc"))
            kotlin.srcDir(layout.buildDirectory.dir("generated/source/proto/main/grpckt"))
            kotlin.srcDir(layout.buildDirectory.dir("generated/source/proto/main/kotlin"))
            kotlin.srcDir(layout.buildDirectory.dir("generated/source/proto/main/java"))
        }
    }
}

sourceSets {
    val main by getting {
        // add your proto folder
        proto {
            srcDir("$projectDir/src/main/proto")
        }
    }
}


protobuf {
    protoc {
        artifact = "com.google.protobuf:protoc:4.30.0"
    }
    plugins {
        create("grpc") {
            // Java gRPC stub generator
            artifact = "io.grpc:protoc-gen-grpc-java:1.71.0"
        }
        create("grpckt") {
            // Kotlin gRPC stub generator
            artifact = "io.grpc:protoc-gen-grpc-kotlin:1.4.1:jdk8@jar"
        }
    }
    generateProtoTasks {
        all().forEach { task ->
            task.builtins {
                create("kotlin")    // the Kotlin builtin
            }
            task.plugins {
                create("grpc")      // wire in the Java gRPC plugin
                create("grpckt")    // wire in the Kotlin gRPC plugin
            }
        }
    }
}

tasks.withType<Copy>().configureEach {
    duplicatesStrategy = DuplicatesStrategy.INCLUDE
}

dependencies {

    api("com.fasterxml.jackson.core:jackson-annotations")
    api("com.fasterxml.jackson.core:jackson-databind")
    api("com.fasterxml.jackson.datatype:jackson-datatype-jsr310")
    api("com.kjetland:mbknor-jackson-jsonschema_2.13:1.0.39")
    api("io.airbyte.airbyte-protocol:protocol-models:0.19.0") {
        exclude(group="com.google.guava", module="guava")
        exclude(group="com.google.api-client")
        exclude(group="org.apache.logging.log4j")
        exclude(group="javax.validation")
        exclude(group="org.apache.commons")
        exclude(group="commons-io")
    }
    api("io.github.oshai:kotlin-logging-jvm:7.0.0")
    api("io.micronaut:micronaut-runtime")
    api("org.apache.mina:mina-core:2.0.27") // for fixing vulnerability of sshd-mina
    api("org.apache.sshd:sshd-mina:2.13.2")
    api("org.jetbrains.kotlinx:kotlinx-coroutines-core")
    api("com.google.protobuf:protobuf-kotlin:4.30.0")

    implementation("com.datadoghq:dd-trace-api:1.39.0")
    implementation("com.datadoghq:dd-trace-ot:1.39.0")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin")
    implementation("com.fasterxml.jackson.module:jackson-module-afterburner")
    implementation("info.picocli:picocli:4.7.6")
    implementation("io.micronaut.picocli:micronaut-picocli:5.5.0")
    implementation("jakarta.validation:jakarta.validation-api:3.1.0")
    implementation("org.apache.commons:commons-lang3:3.17.0")
    implementation("org.apache.logging.log4j:log4j-api")
    implementation("org.apache.logging.log4j:log4j-core")
    implementation("org.apache.logging.log4j:log4j-slf4j-impl")
    implementation("org.apache.logging.log4j:log4j-slf4j2-impl")
    implementation("org.apache.logging.log4j:log4j-layout-template-json:2.24.0")
    implementation("org.bouncycastle:bcprov-jdk18on:1.78.1")
    implementation("net.i2p.crypto:eddsa:0.3.0")
    implementation("org.openapi4j:openapi-schema-validator:1.0.7")
    implementation("io.grpc:grpc-kotlin-stub:1.4.1")
    implementation("io.grpc:grpc-protobuf:1.71.0")

    // this is only needed because of exclusions in airbyte-protocol
    runtimeOnly("com.google.guava:guava:33.3.0-jre")
    runtimeOnly("org.apache.commons:commons-compress:1.27.1")

    testFixturesApi("org.jetbrains.kotlin:kotlin-test-junit")
    testFixturesApi("org.jetbrains.kotlin:kotlin-reflect")
    testFixturesApi("org.junit.jupiter:junit-jupiter-api")
    testFixturesApi("org.junit.jupiter:junit-jupiter-params")
    testFixturesApi("org.junit.jupiter:junit-jupiter-engine")
    testFixturesApi("org.testcontainers:testcontainers") {
        exclude(group="org.apache.commons", module="commons-compress")
    }
    testFixturesApi("io.micronaut.test:micronaut-test-core:4.5.0")
    testFixturesApi("io.micronaut.test:micronaut-test-junit5:4.5.0")
    testFixturesApi("io.github.deblockt:json-diff:1.1.0")
}

tasks.test {
    environment=mapOf("PRESENT" to "present-value")
}
