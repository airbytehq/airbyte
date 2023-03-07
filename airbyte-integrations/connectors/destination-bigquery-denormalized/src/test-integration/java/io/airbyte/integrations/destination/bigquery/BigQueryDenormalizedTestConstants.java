/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import io.airbyte.integrations.base.JavaBaseConstants;
import java.nio.file.Path;
import java.util.List;

public class BigQueryDenormalizedTestConstants {

  public static final BigQuerySQLNameTransformer NAME_TRANSFORMER = new BigQuerySQLNameTransformer();
  public static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");
  public static final String CONFIG_DATASET_ID = "dataset_id";
  public static final String CONFIG_PROJECT_ID = "project_id";
  public static final String CONFIG_DATASET_LOCATION = "dataset_location";
  public static final String CONFIG_CREDS = "credentials_json";
  public static final List<String> AIRBYTE_COLUMNS = List.of(JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  public static final String USERS_STREAM_NAME = "users";

  public static final String BIGQUERY_DATETIME_FORMAT = "yyyy-MM-dd'T'HH:mm:ss";

}
