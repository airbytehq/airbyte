/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.azureblobstorage;

public class AzureBlobAdditionalProperties {

  private AzureBlobAdditionalProperties() {

  }

  public static final String LAST_MODIFIED = "_ab_source_file_last_modified";

  public static final String BLOB_NAME = "_ab_source_blob_name";

  public static final String ADDITIONAL_PROPERTIES = "_ab_additional_properties";

}
