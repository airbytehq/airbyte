/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.writer;

import com.fasterxml.jackson.databind.JsonNode;
import java.io.IOException;

public interface CommonWriter {

  void initialize() throws IOException;

  void write(JsonNode formattedData) throws IOException;

  void close(boolean hasFailed) throws Exception;

}
