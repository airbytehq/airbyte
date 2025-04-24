/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output

import io.micronaut.context.annotation.Property
import io.micronaut.context.annotation.PropertySource
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

private const val RULE0 = "${REGEX_CLASSIFIER_PREFIX}.rules[0]"
private const val RULE1 = "${REGEX_CLASSIFIER_PREFIX}.rules[1]"
private const val RULE2 = "${REGEX_CLASSIFIER_PREFIX}.rules[2]"

@MicronautTest
@PropertySource(
    value =
        [
            Property(name = "$RULE0.error", value = "config"),
            Property(name = "$RULE0.pattern", value = "foo"),
            Property(name = "$RULE0.input-example", value = "foobarbaz"),
            Property(name = "$RULE0.group", value = "grouped"),
            Property(name = "$RULE0.output", value = "has foo"),
            Property(
                name = "$RULE0.reference-links",
                value = "https://www.youtube.com/watch?v=xvFZjo5PgG0",
            ),
            Property(name = "$RULE1.error", value = "transient"),
            Property(name = "$RULE1.pattern", value = "bar"),
            Property(name = "$RULE1.input-example", value = "foobarbaz"),
            Property(name = "$RULE2.error", value = "system"),
            Property(name = "$RULE2.pattern", value = "baz"),
            Property(name = "$RULE2.input-example", value = "foobarbaz"),
        ]
)
class RegexExceptionClassifierTest {

    @Inject lateinit var classifier: RegexExceptionClassifier

    @Test
    fun testConfigError() {
        Assertions.assertEquals(
            ConfigError("grouped: has foo\nhttps://www.youtube.com/watch?v=xvFZjo5PgG0"),
            classifier.classify(RuntimeException("foo")),
        )
    }

    @Test
    fun testTransientError() {
        Assertions.assertEquals(
            TransientError("?bar!"),
            classifier.classify(RuntimeException("?bar!")),
        )
    }

    @Test
    fun testSystemError() {
        Assertions.assertEquals(
            SystemError("?baz!"),
            classifier.classify(RuntimeException("?baz!")),
        )
    }

    @Test
    fun testUnclassified() {
        Assertions.assertNull(classifier.classify(RuntimeException("quux")))
    }

    @Test
    fun testRuleOrdering() {
        Assertions.assertEquals(
            ConfigError("grouped: has foo\nhttps://www.youtube.com/watch?v=xvFZjo5PgG0"),
            classifier.classify(RuntimeException("foobarbaz")),
        )
        Assertions.assertEquals(
            TransientError("barbaz"),
            classifier.classify(RuntimeException("barbaz")),
        )
    }

    @Test
    fun testRecursiveRuleOrdering() {
        Assertions.assertEquals(
            ConfigError("grouped: has foo\nhttps://www.youtube.com/watch?v=xvFZjo5PgG0"),
            classifier.classify(RuntimeException("quux", RuntimeException("foobarbaz"))),
        )
        Assertions.assertEquals(
            TransientError("barbaz"),
            classifier.classify(RuntimeException("quux", RuntimeException("barbaz"))),
        )
    }
}
