/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.writer;

import io.airbyte.integrations.destination.s3.S3Format;

public interface GscWriter extends CommonWriter {

  String getFileLocation();

  S3Format getFileFormat();

  String getOutputPath();

}
