/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.azureblobstorage;

import org.testcontainers.containers.GenericContainer;

// Azurite emulator for easier local azure storage development and testing
// https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite?tabs=docker-hub
public class AzureBlobStorageContainer extends GenericContainer<AzureBlobStorageContainer> {

  public AzureBlobStorageContainer() {
    super("mcr.microsoft.com/azure-storage/azurite");
  }

}
