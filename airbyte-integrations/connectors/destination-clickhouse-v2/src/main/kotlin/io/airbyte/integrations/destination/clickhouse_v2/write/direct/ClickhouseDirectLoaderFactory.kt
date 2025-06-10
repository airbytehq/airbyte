/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.DirectLoaderFactory
import jakarta.inject.Singleton

@Singleton
class ClickhouseDirectLoaderFactory(private val clickhouseClient: Client) :
    DirectLoaderFactory<ClickhouseDirectLoader> {
    override val maxNumOpenLoaders = 2

    override fun create(
        streamDescriptor: DestinationStream.Descriptor,
        part: Int
    ): ClickhouseDirectLoader = ClickhouseDirectLoader(streamDescriptor, clickhouseClient)
}
