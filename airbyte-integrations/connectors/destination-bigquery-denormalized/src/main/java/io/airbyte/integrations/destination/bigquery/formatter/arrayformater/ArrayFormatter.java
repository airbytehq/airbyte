/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter.arrayformater;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.List;

public interface ArrayFormatter {

  void populateEmptyArrays(final JsonNode node);

  void surroundArraysByObjects(final JsonNode node);

  JsonNode formatArrayItems(final List<JsonNode> arrayItems);

}
