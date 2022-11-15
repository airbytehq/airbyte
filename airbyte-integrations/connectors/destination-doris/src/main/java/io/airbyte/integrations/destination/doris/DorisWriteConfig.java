/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;

public class DorisWriteConfig {

  private final DorisStreamLoad dorisStreamLoad;
  private final CSVPrinter writer;
  private final CSVFormat format;

  public DorisWriteConfig(DorisStreamLoad dorisStreamLoad, CSVPrinter writer, CSVFormat format) {
    this.dorisStreamLoad = dorisStreamLoad;
    this.writer = writer;
    this.format = format;
  }

  public DorisStreamLoad getDorisStreamLoad() {
    return dorisStreamLoad;
  }

  public CSVFormat getFormat() {
    return format;
  }

  public CSVPrinter getWriter() {
    return writer;
  }

}
