/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc

import io.airbyte.cdk.integrations.destination.jdbc.constants.GlobalDataSizeConstants

/**
 * The staging file is uploaded to cloud storage in multiple parts. This class keeps track of the
 * filename, and returns a new one when the old file has had enough parts.
 */
class StagingFilenameGenerator(private val streamName: String, chunkSize: Long) {
    // the file suffix will change after the max number of file
    // parts have been generated for the current suffix;
    // its value starts from 0.
    private var currentFileSuffix = 0

    // the number of parts that have been generated for the current
    // file suffix; its value range will be [1, maxPartsPerFile]
    private var currentFileSuffixPartCount = 0

    // This variable is responsible to set the size of chunks size (In MB). After chunks created in
    // S3 or GCS they will be uploaded to Snowflake or Redshift. These service have some limitations
    // for
    // the uploading file.
    // So we make the calculation to determine how many parts we can put to the single chunk file.
    private val iterations: Long = GlobalDataSizeConstants.Companion.MAX_FILE_SIZE / chunkSize

    val stagingFilename: String
        /**
         * This method is assumed to be called whenever one part of a file is going to be created.
         * The currentFileSuffix increments from 0. The currentFileSuffixPartCount cycles from 1 to
         * maxPartsPerFile.
         */
        get() {
            if (currentFileSuffixPartCount < iterations) {
                // when the number of parts for the file has not reached the max,
                // keep using the same file (i.e. keep the suffix)
                currentFileSuffixPartCount += 1
            } else {
                // otherwise, reset the part counter, and use a different file
                // (i.e. update the suffix)
                currentFileSuffix += 1
                currentFileSuffixPartCount = 1
            }
            return String.format("%s_%05d", streamName, currentFileSuffix)
        }
}
