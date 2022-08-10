/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import io.airbyte.integrations.destination.StandardNameTransformer;

public class BigQuerySQLNameTransformer extends StandardNameTransformer {

  @Override
  public String convertStreamName(final String input) {
    if (input == null) {
      return null;
    }

    final String result = super.convertStreamName(input);
    if (!result.substring(0, 1).matches("[A-Za-z_]")) {
      // has to start with a letter or _
      return "_" + result;
    }
    return result;
  }

  /**
   * BigQuery allows a number to be the first character of a namespace. Datasets that begin with an
   * underscore are hidden databases, and we cannot query <hidden-dataset>.INFORMATION_SCHEMA. So we
   * append a letter instead of underscore for normalization. Reference:
   * https://cloud.google.com/bigquery/docs/datasets#dataset-naming
   */
  @Override
  public String getNamespace(final String input) {
    if (input == null) {
      return null;
    }

    final String normalizedName = super.convertStreamName(input);
    if (!normalizedName.substring(0, 1).matches("[A-Za-z0-9]")) {
      return BigQueryConsts.NAMESPACE_PREFIX + normalizedName;
    }
    return normalizedName;
  }

}
