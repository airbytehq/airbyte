/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.writer

import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat

interface DestinationFileWriter : DestinationWriter {
    val fileLocation: String

    val fileFormat: FileUploadFormat?

    val outputPath: String
}
