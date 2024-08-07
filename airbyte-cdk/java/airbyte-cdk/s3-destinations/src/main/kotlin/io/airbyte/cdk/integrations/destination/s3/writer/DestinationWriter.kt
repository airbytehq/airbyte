/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.writer

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.io.IOException
import java.util.*

/**
 * [DestinationWriter] is responsible for writing Airbyte stream data to an S3 location in a
 * specific format.
 */
interface DestinationWriter {
    /** Prepare an S3 writer for the stream. */
    @Throws(IOException::class) fun initialize()

    /** Write an Airbyte record message to an S3 object. */
    @Throws(IOException::class) fun write(id: UUID, recordMessage: AirbyteRecordMessage)

    @Throws(IOException::class) fun write(formattedData: JsonNode)

    @Throws(IOException::class)
    fun write(formattedData: String?) {
        write(Jsons.deserialize(formattedData))
    }

    /** Close the S3 writer for the stream. */
    @Throws(IOException::class) fun close(hasFailed: Boolean)

    @Throws(IOException::class)
    fun closeAfterPush() {
        close(false)
    }
}
