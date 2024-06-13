/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc.copy

import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.util.*

/**
 * StreamCopier is responsible for writing to a staging persistence and providing methods to remove
 * the staged data.
 */
interface StreamCopier {
    /** Writes a value to a staging file for the stream. */
    @Throws(Exception::class)
    fun write(id: UUID?, recordMessage: AirbyteRecordMessage?, fileName: String?)

    /**
     * Closes the writer for the stream to the current staging file. The staging file must be of a
     * certain size specified in GlobalDataSizeConstants + one more buffer. The writer for the
     * stream will close with a note that no errors were found.
     */
    @Throws(Exception::class) fun closeNonCurrentStagingFileWriters()

    /**
     * Closes the writer for the stream to the staging persistence. This method should block until
     * all buffered data has been written to the persistence.
     */
    @Throws(Exception::class) fun closeStagingUploader(hasFailed: Boolean)

    /** Creates a temporary table in the target database. */
    @Throws(Exception::class) fun createTemporaryTable()

    /**
     * Copies the staging file to the temporary table. This method should block until the
     * copy/upload has completed.
     */
    @Throws(Exception::class) fun copyStagingFileToTemporaryTable()

    /** Creates the destination schema if it does not already exist. */
    @Throws(Exception::class) fun createDestinationSchema()

    /**
     * Creates the destination table if it does not already exist.
     *
     * @return the name of the destination table
     */
    @Throws(Exception::class) fun createDestinationTable(): String?

    /** Generates a merge SQL statement from the temporary table to the final table. */
    @Throws(Exception::class) fun generateMergeStatement(destTableName: String?): String

    /**
     * Cleans up the copier by removing the staging file and dropping the temporary table after
     * completion or failure.
     */
    @Throws(Exception::class) fun removeFileAndDropTmpTable()

    /**
     * Creates the staging file and all the necessary items to write data to this file.
     *
     * @return A string that unqiuely identifies the file. E.g. the filename, or a unique suffix
     * that is appended to a shared filename prefix
     */
    fun prepareStagingFile(): String

    /** @return current staging file name */
    val currentFile: String?
}
