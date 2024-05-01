/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import com.amazonaws.services.s3.internal.SkipMd5CheckStrategy;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.destination.gcs.BaseGcsDestination;

public class GcsDestination extends BaseGcsDestination {

  public static void main(final String[] args) throws Exception {
    System.setProperty(SkipMd5CheckStrategy.DISABLE_GET_OBJECT_MD5_VALIDATION_PROPERTY, "true");
    System.setProperty(SkipMd5CheckStrategy.DISABLE_PUT_OBJECT_MD5_VALIDATION_PROPERTY, "true");
    new IntegrationRunner(new GcsDestination()).run(args);
  }

}
