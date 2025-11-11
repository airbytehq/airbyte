/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output

import io.micronaut.context.annotation.Property
import io.micronaut.context.annotation.PropertySource
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.sql.SQLException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

private const val RULE1 = "${JDBC_CLASSIFIER_PREFIX}.rules[1]"
private const val RULE2 = "${JDBC_CLASSIFIER_PREFIX}.rules[2]"

@MicronautTest
@PropertySource(
    value =
        [
            // RULE0 is already defined in application.yml
            Property(name = "$RULE1.error", value = "transient"),
            Property(name = "$RULE1.code", value = "123"),
            Property(name = "$RULE1.group", value = "grouped"),
            Property(name = "$RULE2.error", value = "system"),
            Property(name = "$RULE2.code", value = "456"),
        ]
)
class JdbcExceptionClassifierTest {

    @Inject lateinit var classifier: JdbcExceptionClassifier

    @Test
    fun testConfigError() {
        Assertions.assertEquals(
            ConfigError("Connection failure: Database does not exist"),
            classifier.classify(SQLException("foo", "bar", 90149)),
        )
    }

    @Test
    fun testTransientError() {
        Assertions.assertEquals(
            TransientError("grouped: State code: bar; Error code: 123; Message: foo"),
            classifier.classify(SQLException("foo", "bar", 123)),
        )
    }

    @Test
    fun testSystemError() {
        Assertions.assertEquals(
            SystemError("State code: bar; Error code: 456; Message: foo"),
            classifier.classify(SQLException("foo", "bar", 456)),
        )
    }

    @Test
    fun testUnclassified() {
        Assertions.assertEquals(
            SystemError("State code: bar; Error code: 789; Message: foo"),
            classifier.classify(SQLException("foo", "bar", 789)),
        )
    }
}
