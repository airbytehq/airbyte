package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.lang.CloseableQueue;

import java.util.Collection;
import java.util.Iterator;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;

public class CloseableLinkedBlockingQueue extends LinkedBlockingQueue<JsonNode> implements CloseableQueue<JsonNode> {

    private final Runnable onClose;

    public CloseableLinkedBlockingQueue(Runnable onClose) {
        this.onClose = onClose;
    }

    @Override
    public void close() throws Exception {
        onClose.run();
    }
}
