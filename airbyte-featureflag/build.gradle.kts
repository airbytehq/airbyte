import org.jetbrains.kotlin.gradle.dsl.JvmTarget
import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    `java-library`
    kotlin("jvm") version "1.8.0"
    kotlin("kapt") version "1.8.0"
//    id("org.jetbrains.kotlin.plugin.allopen") version "1.8.0"
//    id("io.micronaut.minimal.application") version "3.7.0"
}

dependencies {
//    annotationProcessor(platform(libs.micronaut.bom))
//    annotationProcessor(libs.bundles.micronaut.annotation.processor)
    kapt(platform(libs.micronaut.bom))
    kapt(libs.bundles.micronaut.annotation.processor)

    implementation(platform(libs.micronaut.bom))
    implementation("io.micronaut:micronaut-core:3.8.2")
    implementation(libs.micronaut.inject)
    implementation("io.micronaut.kotlin:micronaut-kotlin-runtime")
    implementation(libs.launchdarkly)
    implementation(libs.jackson.databind)
    implementation(libs.jackson.dataformat)
    implementation(libs.jackson.kotlin)

//    testAnnotationProcessor(platform(libs.micronaut.bom))
//    testAnnotationProcessor(libs.bundles.micronaut.test.annotation.processor)
    kaptTest(platform(libs.micronaut.bom))
    kaptTest(libs.bundles.micronaut.test.annotation.processor)

    testImplementation(kotlin("test"))
    testImplementation(kotlin("test-junit5"))
    testImplementation("com.github.spotbugs:spotbugs-annotations:4.7.3")
    testImplementation(libs.bundles.micronaut.test)
    testImplementation(libs.mockk)
    testImplementation(libs.bundles.junit)
}

tasks.withType<KotlinCompile> {
    compilerOptions {
        jvmTarget.set(JvmTarget.JVM_17)
    }
}

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

tasks.test {
    useJUnitPlatform()
}

//micronaut {
//    version("3.8.2")
//    processing {
//        annotations("io.airbyte.*")
//    }
//}
