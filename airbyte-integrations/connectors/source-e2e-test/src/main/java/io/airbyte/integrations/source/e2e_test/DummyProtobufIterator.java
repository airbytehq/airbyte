/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.google.protobuf.ByteString;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.AirbyteRecord;
import io.airbyte.protocol.Protocol;
import java.time.Instant;
import java.util.concurrent.atomic.AtomicLong;

public class DummyProtobufIterator implements AutoCloseableIterator<Protocol.AirbyteMessage> {

  private static final long MAX_RECORDS = 50_000_000;
  private static final String STREAM = "stream1";
  private static final String DATA =
      "{\"field1\":\"valuevaluevaluevaluevalue1\",\"field2\":\"valuevaluevaluevaluevalue1\",\"field3\":\"valuevaluevaluevaluevalue1\",\"field4\":\"valuevaluevaluevaluevalue1\",\"field5\":\"valuevaluevaluevaluevalue1\",}";
  private static final Protocol.AirbyteMessage CONSTANT_MESSAGE = Protocol.AirbyteMessage.newBuilder()
      .setType(Protocol.AirbyteMessageType.RECORD)
      .setRecord(AirbyteRecord.AirbyteRecordMessage.newBuilder()
          .setData(ByteString.copyFromUtf8(DATA))
          .setStream(STREAM)
          .setEmittedAt(Instant.now().toEpochMilli())
          .build())
      .build();

  private final AtomicLong counter = new AtomicLong(0);

  @Override
  public void close() {

  }

  @Override
  public boolean hasNext() {
    return counter.get() <= MAX_RECORDS;
  }

  @Override
  public Protocol.AirbyteMessage next() {
    counter.getAndIncrement();
    return CONSTANT_MESSAGE;
  }

}
