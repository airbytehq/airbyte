/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.writer;

import io.airbyte.cdk.integrations.destination.s3.S3Format;

public interface DestinationFileWriter extends DestinationWriter {

  String getFileLocation();

  S3Format getFileFormat();

  String getOutputPath();

}
