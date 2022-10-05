/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

public interface DbtCloudClient {

  String triggerRun(String jobId);

}
