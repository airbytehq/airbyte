import org.jetbrains.kotlin.gradle.dsl.JvmTarget
import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    `java-library`
    kotlin("jvm") version "1.8.0"
}

dependencies {
    annotationProcessor(platform(libs.micronaut.bom))
    annotationProcessor(libs.bundles.micronaut.annotation.processor)

    implementation(platform(libs.micronaut.bom))
    implementation(libs.micronaut.inject)
    implementation("com.jayway.jsonpath:json-path:2.7.0")
    implementation("com.launchdarkly:launchdarkly-java-server-sdk:6.0.1")
    implementation("com.fasterxml.jackson.core:jackson-databind:2.14.0")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin:2.14.0")
    implementation("com.fasterxml.jackson.dataformat:jackson-dataformat-yaml:2.14.0")

    testAnnotationProcessor(platform(libs.micronaut.bom))
    testAnnotationProcessor(libs.micronaut.inject)
    testAnnotationProcessor(libs.bundles.micronaut.test.annotation.processor)

    testImplementation(libs.bundles.micronaut.test)
    testImplementation("io.mockk:mockk:1.13.3")
    testImplementation(libs.bundles.junit)
}

tasks.withType<KotlinCompile> {
    compilerOptions {
        jvmTarget.set(JvmTarget.JVM_17)
    }
}

tasks.test {
    useJUnitPlatform()
}