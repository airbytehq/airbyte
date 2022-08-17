/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.jdbc.DataAdapter;

public class TeradataDataAdapter extends DataAdapter {

  public TeradataDataAdapter() {
    super(jsonNode -> jsonNode.isTextual() && jsonNode.textValue().contains("\u0000"),
        jsonNode -> {
          final String textValue = jsonNode.textValue().replaceAll("\\u0000", "");
          return Jsons.jsonNode(textValue);
        });
  }

}

