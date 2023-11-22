package io.airbyte.cdk.integrations.base.io;

import io.airbyte.commons.json.Jsons;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.PrintWriter;
import java.net.Socket;
import java.util.function.Consumer;

public class SocketOutputRecordCollector<T> implements Consumer<T>, AutoCloseable {

    private static final Logger LOGGER = LoggerFactory.getLogger(SocketOutputRecordCollector.class);

    private final String host;
    private final Integer port;
    private final Integer retryBackoffMs;
    private Socket socket;
    private PrintWriter writer;

    public SocketOutputRecordCollector(final String host, final Integer port, final Integer retryBackoffMs) {
        this.host = host;
        this.port = port;
        this.retryBackoffMs = retryBackoffMs;
    }

    public void connect() {
        boolean connected = false;
        while(!connected) {
            try {
                LOGGER.info("Attempting to connect to platform at {}:{}...", host, port);
                socket = new Socket(host, port);
                writer = new PrintWriter(socket.getOutputStream(), true);
                connected = true;
                LOGGER.info("Successfully connected to platform at {}:{}.", host, port);
            } catch (IOException e) {
                LOGGER.warn("Unable to connect to platform at {}:{}.  Attempting to re-connect in {} milliseconds...", host, port, retryBackoffMs, e);
                try {
                    Thread.sleep(retryBackoffMs);
                } catch (InterruptedException ex) {
                    LOGGER.warn("Connection backoff interrupted.", e);
                }
            }
        }
    }

    @Override
    public void accept(final T airbyteMessage) {
        final String messageAsJson = Jsons.serialize(airbyteMessage);
        if (writer != null) {
            writer.println(messageAsJson);
            writer.flush();
        } else {
            LOGGER.warn("Unable to write message '{}' as the writer has not been initialized.", messageAsJson);
        }
    }

    @Override
    public void close() throws Exception {
        if (writer != null) {
            writer.flush();
            writer.close();
        }
        if (socket != null && !socket.isClosed()) {
            socket.close();
        }
    }
}
