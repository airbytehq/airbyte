/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.initialization

import io.micronaut.context.annotation.Bean
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

@MicronautTest
class TestApplicationYaml {
    @Inject lateinit var defaultValueBean: DefaultValueBean

    @Test
    fun testMainDefaultValue() {
        assertEquals("/staging/files", defaultValueBean.stagingFolder)
        assertEquals(false, defaultValueBean.fileTransferEnable)
    }
}

data class DefaultValueBean(
    val stagingFolder: String,
    val fileTransferEnable: Boolean,
)

@Factory
class TestFactory {
    @Bean
    fun defaultValueBean(
        @Value("\${airbyte.destination.core.file-transfer.staging-path}") stagingFolder: String,
        @Value("\${airbyte.destination.core.file-transfer.enabled}") fileTransferEnable: Boolean,
    ): DefaultValueBean {
        return DefaultValueBean(stagingFolder, fileTransferEnable)
    }
}
