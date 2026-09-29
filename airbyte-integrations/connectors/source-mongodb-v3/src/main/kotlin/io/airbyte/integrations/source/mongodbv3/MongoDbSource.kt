/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import io.airbyte.cdk.AirbyteSourceRunner

object MongoDbSource {
    @JvmStatic fun main(args: Array<String>) = AirbyteSourceRunner.run(*args)
}
