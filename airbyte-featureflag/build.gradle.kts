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
    implementation(libs.launchdarkly)
    implementation(libs.jackson.databind)
    implementation(libs.jackson.dataformat)
    implementation(libs.jackson.kotlin)

    testAnnotationProcessor(platform(libs.micronaut.bom))
    testAnnotationProcessor(libs.micronaut.inject)
    testAnnotationProcessor(libs.bundles.micronaut.test.annotation.processor)

    testImplementation(kotlin("test"))
    testImplementation(kotlin("test-junit5"))
    testImplementation(libs.bundles.micronaut.test)
    testImplementation(libs.mockk)
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
