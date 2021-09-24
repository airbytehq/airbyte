/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.credential;

public interface GcsCredentialConfig {

  GcsCredential getCredentialType();

}
