/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_glue;

import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.util.Stringify;

public interface MetastoreFormatConfig extends S3FormatConfig {

  String getInputFormat();

  String getOutputFormat();

  String getSerializationLibrary();

  Stringify getStringifyType();

}
