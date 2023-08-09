/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.selectdb;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;

public class SelectdbWriteConfig {

  private final SelectdbCopyInto selectdbCopyInto;
  private final CSVPrinter writer;
  private final CSVFormat format;

  public SelectdbWriteConfig(SelectdbCopyInto sci, CSVPrinter writer, CSVFormat format) {
    this.selectdbCopyInto = sci;
    this.writer = writer;
    this.format = format;
  }

  public SelectdbCopyInto getsci() {
    return selectdbCopyInto;
  }

  public CSVFormat getFormat() {
    return format;
  }

  public CSVPrinter getWriter() {
    return writer;
  }

}
