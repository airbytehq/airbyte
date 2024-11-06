/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.initialization

import io.micronaut.context.annotation.Bean
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Test

@MicronautTest
class TestApplicationYaml {
    @Inject lateinit var testBean: TestBean

    @Test
    fun testApplicationYamlInjection() {
        assert(testBean.testApplicationYamlEntry == "value")
        assert(testBean.testDefault == "default")
        assert(testBean.testEnv == "present-value")
    }
}

data class TestBean(
    val testApplicationYamlEntry: String,
    val testDefault: String,
    val testEnv: String
)

@Factory
class TestFactory {
    @Bean
    fun testBean(
        @Value("\${airbyte.test}") testValue: String,
        @Value("\${airbyte.test-default}") testDefault: String,
        @Value("\${airbyte.test-env}") testEnv: String
    ): TestBean {
        return TestBean(testValue, testDefault, testEnv)
    }
}
