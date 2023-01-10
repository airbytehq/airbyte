package io.airbyte.workers.internal;

import datadog.trace.api.Trace;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.airbyte.metrics.lib.OssMetricsRegistry;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.general.DefaultReplicationWorker;
import io.airbyte.workers.internal.exception.SourceException;

import java.io.BufferedReader;
import java.nio.charset.StandardCharsets;
import java.util.stream.Stream;

import static io.airbyte.metrics.lib.ApmTraceConstants.WORKER_OPERATION_NAME;

public class SourceStreamFactory extends DefaultAirbyteStreamFactory {

    public SourceStreamFactory(MdcScope.Builder containerLogMdcBuilder) {
        super(containerLogMdcBuilder);
    }

    @Trace(operationName = WORKER_OPERATION_NAME)
    @Override
    public Stream<AirbyteMessage> create(final BufferedReader bufferedReader) {
        final var metricClient = MetricClientFactory.getMetricClient();
        return bufferedReader
                .lines()
                .peek(str -> metricClient.distribution(OssMetricsRegistry.JSON_STRING_LENGTH, str.length()))
                .peek(str -> {
                    long messageSize = str.getBytes(StandardCharsets.UTF_8).length;
                    if (messageSize > /**/1L/**//*Runtime.getRuntime().maxMemory() * 0.6/**/) {
                        throw new SourceException("too big message");
                    }
                })
                .flatMap(this::parseJson)
                .filter(this::validate)
                .flatMap(this::toAirbyteMessage)
                .filter(this::filterLog);
    }
}
