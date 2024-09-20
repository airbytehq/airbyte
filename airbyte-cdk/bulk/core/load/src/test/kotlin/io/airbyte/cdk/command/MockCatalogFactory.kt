/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command

import io.airbyte.cdk.data.FieldType
import io.airbyte.cdk.data.IntegerType
import io.airbyte.cdk.data.ObjectType
import io.airbyte.cdk.data.StringType
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Factory
@Replaces(factory = DestinationCatalogFactory::class)
@Requires(env = ["test"])
class MockCatalogFactory : DestinationCatalogFactory {
    companion object {
        val stream1 =
            DestinationStream(
                DestinationStream.Descriptor("test", "stream1"),
                importType = Append,
                schema =
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "id" to FieldType(type = IntegerType, nullable = true),
                                "name" to FieldType(type = StringType, nullable = true),
                            ),
                    ),
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 42,
            )
        val stream2 =
            DestinationStream(
                DestinationStream.Descriptor("test", "stream2"),
                importType = Append,
                schema =
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "id" to FieldType(type = IntegerType, nullable = true),
                                "name" to FieldType(type = StringType, nullable = true),
                            ),
                    ),
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 42,
            )
    }

    @Singleton
    @Named("mockCatalog")
    override fun make(): DestinationCatalog {
        return DestinationCatalog(streams = listOf(stream1, stream2))
    }
}
