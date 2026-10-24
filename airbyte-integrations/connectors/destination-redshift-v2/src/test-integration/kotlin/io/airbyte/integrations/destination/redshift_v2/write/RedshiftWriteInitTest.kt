/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.write

import io.airbyte.cdk.load.write.WriteInitializationTest
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2Specification
import java.nio.file.Files
import java.nio.file.Path

class RedshiftWriteInitTest :
    WriteInitializationTest<RedshiftV2Specification>(
        configContents = Files.readString(Path.of("secrets/config_staging.json")),
        configSpecClass = RedshiftV2Specification::class.java,
    )
