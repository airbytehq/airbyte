/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.write

import io.airbyte.cdk.load.write.WriteInitializationTest
import io.airbyte.integrations.destination.mongodb_v2.config.MongodbSpecification
import java.nio.file.Path

class MongodbWriteInitTest : WriteInitializationTest<MongodbSpecification>(
    configContents = Path.of("secrets/config.json").toFile().readText(),
    configSpecClass = MongodbSpecification::class.java,
)
