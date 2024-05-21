package io.airbyte.integrations.source.mysql;

import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.commons.stream.AirbyteStreamStatusHolder;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class StreamStatusTraceEmitterIterator implements AutoCloseableIterator<AirbyteMessage> {
    private static final Logger LOGGER = LoggerFactory.getLogger(StreamStatusTraceEmitterIterator.class);
    private boolean emitted = false;
    private AirbyteStreamStatusHolder statusHolder;

    public StreamStatusTraceEmitterIterator(final AirbyteStreamStatusHolder statusHolder) {
        this.statusHolder = statusHolder;
    }
    @Override
    public boolean hasNext() {
        return !emitted;
    }

    @Override
    public AirbyteMessage next() {
        emitted = true;
        return AirbyteTraceMessageUtility.INSTANCE.makeStreamStatusTraceAirbyteMessage(statusHolder);
    }

    @Override
    public void close() throws Exception {
        // no-op
    }

    @Override
    public void remove() {
        //no-op
    }
}
