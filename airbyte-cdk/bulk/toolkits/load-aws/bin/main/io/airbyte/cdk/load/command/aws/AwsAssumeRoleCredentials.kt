/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.aws

import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import io.micronaut.context.condition.Condition
import io.micronaut.context.condition.ConditionContext
import javax.inject.Singleton

// For some reason, micronaut doesn't handle plain `@Requires(property = "...")` when you declare
// the application.yaml as `foo: ${FOO_BAR}`.
// If the env var is unset, it sees the property as existing (and thus satisfying the Requires)
// but then tries to inject a null value to the field, which obviously throws an exception.
// So instead, we declare the property as `${FOO_BAR:}` (i.e. default to empty string)
// and set a property notEquals empty string requirement.

// You might expect that after dealing with that mess, we could just declare three @Requires flags,
// like so:
// @Requires(property = ACCESS_KEY_PROPERTY, notEquals = "")
// @Requires(property = SECRET_KEY_PROPERTY, notEquals = "")
// @Requires(property = EXTERNAL_ID_PROPERTY, notEquals = "")

// However, micronaut sometimes decides to not load the bean, when there are three different
// @Requires annotations.
// So instead we define a custom condition, which does the _exact same thing_,
// but lets us use only a single Requires annotation.
@Requires(condition = AssumeRoleCredentialsCondition::class)
@Singleton
data class AwsAssumeRoleCredentials(
    @Value("\${$ACCESS_KEY_PROPERTY}") val accessKey: String,
    @Value("\${$SECRET_KEY_PROPERTY}") val secretKey: String,
    @Value("\${$EXTERNAL_ID_PROPERTY}") val externalId: String,
) {
    override fun toString() = "AwsAssumeRoleCredentials(<redacted>)"
}

const val ACCESS_KEY_PROPERTY = "airbyte.destination.aws.assume-role.access-key"
const val SECRET_KEY_PROPERTY = "airbyte.destination.aws.assume-role.secret-key"
const val EXTERNAL_ID_PROPERTY = "airbyte.destination.aws.assume-role.external-id"

private object AssumeRoleCredentialsCondition : Condition {
    override fun matches(context: ConditionContext<*>): Boolean {
        val accessKey = context.getProperty(ACCESS_KEY_PROPERTY, String::class.java).orElse("")
        val secretKey = context.getProperty(SECRET_KEY_PROPERTY, String::class.java).orElse("")
        val externalId = context.getProperty(EXTERNAL_ID_PROPERTY, String::class.java).orElse("")

        return accessKey.isNotEmpty() && secretKey.isNotEmpty() && externalId.isNotEmpty()
    }
}
