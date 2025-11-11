/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.aws

import io.airbyte.cdk.load.command.Property

object AwsEnvVarConstants {
    val ASSUME_ROLE_ACCESS_KEY = Property(ACCESS_KEY_PROPERTY, "AWS_ACCESS_KEY_ID")
    val ASSUME_ROLE_SECRET_KEY = Property(SECRET_KEY_PROPERTY, "AWS_SECRET_ACCESS_KEY")
    val ASSUME_ROLE_EXTERNAL_ID = Property(EXTERNAL_ID_PROPERTY, "AWS_ASSUME_ROLE_EXTERNAL_ID")
}
