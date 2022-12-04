/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.jdbc.DataAdapter;

public class PostgresDataAdapter extends DataAdapter {

  public PostgresDataAdapter() {
    super(jsonNode -> jsonNode.isTextual() && jsonNode.textValue().contains("\u0000"),
        jsonNode -> {
          final String textValue = jsonNode.textValue().replaceAll("\\u0000", "");
          return Jsons.jsonNode(textValue);
        });
  }

}
