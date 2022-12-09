/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.validation.json.JsonValidationException;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import java.io.IOException;
import java.util.UUID;

@ActivityInterface
public interface RefreshSchemaActivity {

  @ActivityMethod
  boolean shouldRefreshSchema(UUID sourceCatalogId) throws IOException;

  public void refreshSchema(UUID sourceCatalogId) throws JsonValidationException, ConfigNotFoundException, IOException, ApiException;

}
