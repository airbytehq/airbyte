/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import io.airbyte.commons.util.AutoCloseableIterator;
import java.nio.charset.Charset;
import java.util.concurrent.atomic.AtomicLong;

public class NoSerializationIterator implements AutoCloseableIterator<String> {

  public static final String CONSTANT_JSON_MESSAGE = """
                                                     {
                                                         "type": "RECORD",
                                                         "record": {
                                                             "stream": "stream1",
                                                             "emittedAt": 1742822436065,
                                                             "data": {
                                                                 "field1": "valuevaluevaluevalue1",
                                                                 "field2": "valuevaluevaluevalue1",
                                                                 "field3": "valuevaluevaluevalue1",
                                                                 "field4": "valuevaluevaluevalue1",
                                                                 "field5": "valuevaluevaluevalue1",
                                                             }
                                                         }
                                                     }""";
  public static final long MAX_RECORDS = 50_000_000;

  private final AtomicLong counter = new AtomicLong(0);
  private final AtomicLong totalBytes = new AtomicLong(0);

  @Override
  public void close() {
    System.out.println("Total bytes: " + totalBytes.get());
  }

  @Override
  public boolean hasNext() {
    return counter.get() <= MAX_RECORDS;
  }

  @Override
  public String next() {
    counter.getAndIncrement();
    totalBytes.getAndAdd(CONSTANT_JSON_MESSAGE.getBytes(Charset.defaultCharset()).length);
    return CONSTANT_JSON_MESSAGE;
  }

}
