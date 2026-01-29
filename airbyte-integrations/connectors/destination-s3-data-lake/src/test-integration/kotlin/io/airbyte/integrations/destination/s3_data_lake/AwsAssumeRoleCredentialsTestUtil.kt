/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.Property
import io.airbyte.cdk.load.command.aws.AwsAssumeRoleCredentials
import io.airbyte.cdk.load.command.aws.AwsEnvVarConstants

fun AwsAssumeRoleCredentials.asMicronautProperties(): Map<Property, String> =
    mapOf(
        AwsEnvVarConstants.ASSUME_ROLE_ACCESS_KEY to accessKey,
        AwsEnvVarConstants.ASSUME_ROLE_SECRET_KEY to secretKey,
        AwsEnvVarConstants.ASSUME_ROLE_EXTERNAL_ID to externalId,
    )
