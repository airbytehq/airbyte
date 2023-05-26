package io.airbyte.integrations.destination_performance;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.time.Instant;
import java.util.Random;
import javax.annotation.CheckForNull;

/**
 * This iterator generates test data to be used in speed benchmarking at airbyte. It is
 * deterministic--if called with the same constructor values twice, it will return the same data.
 * The goal is for it to go fast.
 */
public class PerfBenchmarkGeneratorIterator extends AbstractIterator<AirbyteMessage> {

    private static final String fieldBase = "field";
    private static final String valueBase = "valuevaluevaluevaluevalue";
    private static final AirbyteMessage message = new AirbyteMessage()
            .withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withEmittedAt(Instant.EPOCH.toEpochMilli()));
    private static final JsonNode jsonNode = Jsons.emptyObject();

    private final long maxRecords;
    private final int numberOfStreams;
    // Uses a seed to get determinisitic results
    private final Random random = new Random(54321);
    private long numRecordsEmitted;
    private final int NUMBER_OF_VALUES = 5;
    private final String namespace;

    public PerfBenchmarkGeneratorIterator(final long maxRecords, final int numberOfStreams, final String namespace) {
        this.maxRecords = maxRecords;
        this.numberOfStreams = numberOfStreams;
        this.namespace = namespace;
        numRecordsEmitted = 0;
    }

    @CheckForNull
    @Override
    protected AirbyteMessage computeNext() {
        if (numRecordsEmitted == maxRecords) {
            return endOfData();
        }

        numRecordsEmitted++;

        for (int j = 1; j <= NUMBER_OF_VALUES; ++j) {
            // do % 10 so that all records are same length.
            ((ObjectNode) jsonNode).put(fieldBase + j, valueBase + numRecordsEmitted % 10);
        }

        // Ensure the stream name is the same as the benchmark_catalog.json
        // TODO: (ryankfu) wire this in so that it will eventually just pulling in the same as the catalog we're pulling
        final int streamNumber = random.nextInt(numberOfStreams);
        message.getRecord()
                .withData(jsonNode)
                .withStream("users_benchmark" + (streamNumber == 0 ? "" : String.valueOf(streamNumber)))
                .withNamespace(namespace);
        return Jsons.clone(message);
    }

}

