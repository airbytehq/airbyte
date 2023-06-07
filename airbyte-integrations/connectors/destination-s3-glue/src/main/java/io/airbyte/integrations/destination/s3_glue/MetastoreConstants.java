/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_glue;

public class MetastoreConstants {

  private MetastoreConstants() {

  }

  public static final String GLUE_DATABASE = "glue_database";

  public static final String SERIALIZATION_LIBRARY = "glue_serialization_library";

  public static final String TEXT_INPUT_FORMAT = "org.apache.hadoop.mapred.TextInputFormat";

  public static final String TEXT_OUTPUT_FORMAT = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat";

}
