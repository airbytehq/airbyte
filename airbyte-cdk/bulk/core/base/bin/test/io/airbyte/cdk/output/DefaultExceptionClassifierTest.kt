/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.TransientErrorException
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest
class DefaultExceptionClassifierTest {

    @Inject lateinit var classifier: DefaultExceptionClassifier

    @Test
    fun testConfigError() {
        Assertions.assertEquals(
            ConfigError("foo"),
            classifier.classify(ConfigErrorException("foo")),
        )
    }

    @Test
    fun testTransientError() {
        Assertions.assertEquals(
            TransientError("bar"),
            classifier.classify(TransientErrorException("bar")),
        )
    }

    @Test
    fun testSystemError() {
        Assertions.assertEquals(
            SystemError("baz"),
            classifier.classify(SystemErrorException("baz")),
        )
    }

    @Test
    fun testUnclassified() {
        Assertions.assertNull(classifier.classify(RuntimeException("quux")))
    }
}
