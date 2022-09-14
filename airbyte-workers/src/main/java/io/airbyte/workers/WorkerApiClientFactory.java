/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.api.client.AirbyteApiClient;

public interface WorkerApiClientFactory {

  AirbyteApiClient create();

}
