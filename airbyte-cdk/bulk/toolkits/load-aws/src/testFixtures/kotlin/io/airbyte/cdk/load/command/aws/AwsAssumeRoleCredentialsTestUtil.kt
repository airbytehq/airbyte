/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.aws

import io.airbyte.cdk.load.test.util.destination_process.Property

fun AwsAssumeRoleCredentials.asMicronautProperties(): Map<Property, String> =
    mapOf(
        Property(ACCESS_KEY_PROPERTY, "AWS_ACCESS_KEY_ID") to accessKey,
        Property(SECRET_KEY_PROPERTY, "AWS_SECRET_ACCESS_KEY") to secretKey,
        Property(EXTERNAL_ID_PROPERTY, "AWS_ASSUME_ROLE_EXTERNAL_ID") to externalId,
    )
