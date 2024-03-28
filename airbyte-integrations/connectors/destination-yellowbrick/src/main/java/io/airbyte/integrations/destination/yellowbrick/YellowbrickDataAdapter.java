/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.yellowbrick;

import io.airbyte.cdk.integrations.destination.jdbc.DataAdapter;
import io.airbyte.commons.json.Jsons;

public class YellowbrickDataAdapter extends DataAdapter {

  public YellowbrickDataAdapter() {
    super(jsonNode -> jsonNode.isTextual() && jsonNode.textValue().contains("\u0000"),
        jsonNode -> {
          final String textValue = jsonNode.textValue().replaceAll("\\u0000", "");
          return Jsons.jsonNode(textValue);
        });
  }

}
