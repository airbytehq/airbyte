/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.selectdb;

import java.util.UUID;

public class LabelInfo {

  private String prefix;

  private String table;

  public LabelInfo(String labelPrefix, String table) {
    this.prefix = labelPrefix;
    this.table = table;
  }

  public String label() {
    return prefix + "_" + table + "_" + UUID.randomUUID() + System.currentTimeMillis();
  }

}
