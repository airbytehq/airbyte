package io.airbyte.integrations.base.output;

/**
 * Factory class for obtaining an {@link OutputRecordConsumer}.
 */
public class OutputRecordConsumerFactory {

    private OutputRecordConsumerFactory() {}

    public static OutputRecordConsumer getOutputRecordConsumer() {
        return new PrintWriterOutputRecordConsumer();
    }
}
