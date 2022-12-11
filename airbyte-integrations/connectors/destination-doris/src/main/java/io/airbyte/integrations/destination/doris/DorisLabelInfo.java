/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris;

import java.util.UUID;

public class DorisLabelInfo {

  private String prefix;

  private String table;

  private boolean enable2PC;

  public DorisLabelInfo(String labelPrefix, String table, boolean enable2PC) {
    this.prefix = labelPrefix;
    this.table = table;
    this.enable2PC = enable2PC;
  }

  public String label() {
    return prefix + "_" + table + "_" + UUID.randomUUID() + System.currentTimeMillis();
  }

  public String label(long chkId) {
    return prefix + "_" + chkId;
  }

}
