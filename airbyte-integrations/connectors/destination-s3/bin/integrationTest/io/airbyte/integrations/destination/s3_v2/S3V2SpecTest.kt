/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.command.aws.asMicronautProperties
import io.airbyte.cdk.load.spec.SpecTest

class S3V2SpecTest :
    SpecTest(micronautProperties = S3V2TestUtils.assumeRoleCredentials.asMicronautProperties())
