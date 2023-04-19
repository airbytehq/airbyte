/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

/**
 * Represents storage provider type
 */
public enum StorageProvider {
  AWS_S3,
  CF_R2;
}
