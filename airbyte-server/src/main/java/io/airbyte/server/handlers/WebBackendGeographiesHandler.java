/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.generated.Geography;
import io.airbyte.api.model.generated.WebBackendGeographiesListResult;
import java.util.Arrays;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@AllArgsConstructor
@Slf4j
public class WebBackendGeographiesHandler {

  /**
   * Returns all available Geography settings that can be set on a Workspace or Connection.
   *
   * @return result containing list of geographies
   */
  public WebBackendGeographiesListResult listGeographies() {
    return new WebBackendGeographiesListResult().geographies(
        Arrays.stream(Geography.values()).toList());
  }

}
