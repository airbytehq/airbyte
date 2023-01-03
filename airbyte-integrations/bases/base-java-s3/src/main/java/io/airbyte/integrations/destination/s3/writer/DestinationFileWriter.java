/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.writer;

import io.airbyte.integrations.destination.s3.S3Format;

public interface DestinationFileWriter extends DestinationWriter {

  String getFileLocation();

  S3Format getFileFormat();

  String getOutputPath();

}
