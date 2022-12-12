/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.connectorbuilder.controllers;

import java.util.Map;
import java.util.Optional;

public class StreamReadRequestBody {

  public Map<String, Object> manifest;
  public String stream;
  public Map<String, Object> config;
  public Optional<Map<String, Object>> state;

}
