/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.output;

/**
 * Factory class for obtaining an {@link OutputRecordConsumer}.
 */
public class OutputRecordConsumerFactory {

  private OutputRecordConsumerFactory() {}

  /**
   * Constructs a new {@link OutputRecordConsumer}.
   *
   * @return A new {@link OutputRecordConsumer} instance.
   */
  public static OutputRecordConsumer getOutputRecordConsumer() {
    return new PrintWriterOutputRecordConsumer();
  }

}
