/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

public record PreSignedUrl(String url, long expirationTimeMillis) {

}
