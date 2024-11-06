/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.initialization

import io.micronaut.context.annotation.Bean
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST])
class TestApplicationYaml {
    @Inject lateinit var testBean: TestBean
    @Inject lateinit var defaultValueBean: DefaultValueBean

    @Test
    fun testApplicationYamlInjection() {
        assert(testBean.testApplicationYamlEntry == "value")
        assert(testBean.testDefault == "default")
        assert(testBean.testEnv == "present-value")
    }

    @Test
    fun testMainDefaultValue() {
        assertEquals("/staging/files", defaultValueBean.stagingFolder)
        assertEquals(false, defaultValueBean.fileTransferEnable)
    }
}

data class TestBean(
    val testApplicationYamlEntry: String,
    val testDefault: String,
    val testEnv: String
)

data class DefaultValueBean(
    val stagingFolder: String,
    val fileTransferEnable: Boolean,
)

@Factory
class TestFactory {
    @Bean
    fun testBean(
        @Value("\${airbyte.test}") testValue: String,
        @Value("\${airbyte.test-default}") testDefault: String,
        @Value("\${airbyte.test-env}") testEnv: String,
    ): TestBean {
        return TestBean(testValue, testDefault, testEnv)
    }

    @Bean
    fun defaultValueBean(
        @Value("\${airbyte.file-transfer.staging-folder}") stagingFolder: String,
        @Value("\${airbyte.file-transfer.enabled}") fileTransferEnable: Boolean,
    ): DefaultValueBean {
        return DefaultValueBean(stagingFolder, fileTransferEnable)
    }
}
