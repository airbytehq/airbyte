/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output

import io.airbyte.cdk.TransientErrorException
import io.micronaut.context.annotation.Property
import io.micronaut.context.annotation.PropertySource
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

private const val RULE0 = "${REGEX_CLASSIFIER_PREFIX}.rules[0]"

@MicronautTest
@PropertySource(
    value =
        [
            Property(name = "$RULE0.error", value = "config"),
            Property(name = "$RULE0.pattern", value = "foo"),
            Property(name = "$RULE0.input-example", value = "foobarbaz"),
        ]
)
class ExceptionHandlerTest {

    @Inject lateinit var handler: ExceptionHandler

    @Test
    fun testClassified() {
        Assertions.assertEquals(
            TransientError("foo"),
            handler.classify(TransientErrorException("foo"))
        )
        Assertions.assertEquals(ConfigError("foo"), handler.classify(RuntimeException("foo")))
    }

    @Test
    fun testUnclassified() {
        Assertions.assertEquals(SystemError("quux"), handler.classify(RuntimeException("quux")))
        Assertions.assertEquals(SystemError(null), handler.classify(RuntimeException()))
    }
}
