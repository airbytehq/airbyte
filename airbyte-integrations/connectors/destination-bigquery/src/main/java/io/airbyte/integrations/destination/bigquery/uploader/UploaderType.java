/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader;

public enum UploaderType {
  STANDARD,
  AVRO,
  CSV
}
