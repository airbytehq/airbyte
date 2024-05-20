package io.airbyte.integrations.source.mysql;

import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.stream.AirbyteStreamStatusHolder;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage;
import io.airbyte.protocol.models.v0.AirbyteTraceMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.function.Consumer;

public class StatusEmitterIterator implements AutoCloseableIterator<AirbyteMessage> {
    private static final Logger LOGGER = LoggerFactory.getLogger(StatusEmitterIterator.class);
    private boolean emitted = false;
    private AirbyteStreamStatusHolder statusHolder;

    public StatusEmitterIterator(final AirbyteStreamStatusHolder statusHolder) {
        this.statusHolder = statusHolder;
    }
    @Override
    public boolean hasNext() {
        return !emitted;
    }

    @Override
    public AirbyteMessage next() {
        emitted = true;
        LOGGER.info("*** trace status: {}", Jsons.serialize(statusHolder.toTraceMessage()));
        return AirbyteTraceMessageUtility.INSTANCE.makeStreamStatusTraceAirbyteMessage(statusHolder);

    }

    @Override
    public void close() throws Exception {
        // no-op
    }

    @Override
    public void remove() {

    }
}
