/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.aws

import io.airbyte.cdk.load.command.Property

fun AwsAssumeRoleCredentials.asMicronautProperties(): Map<Property, String> =
    mapOf(
        AwsEnvVarConstants.ASSUME_ROLE_ACCESS_KEY to accessKey,
        AwsEnvVarConstants.ASSUME_ROLE_SECRET_KEY to secretKey,
        AwsEnvVarConstants.ASSUME_ROLE_EXTERNAL_ID to externalId,
    )
