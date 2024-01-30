package io.airbyte.cdk.integrations.base.consumers;

import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer;
import jakarta.inject.Singleton;

import java.io.BufferedInputStream;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;

@Singleton
public class WriteStreamConsumer {

    public void consumeWriteStream(final SerializedAirbyteMessageConsumer consumer) throws Exception {
        try (final BufferedInputStream bis = new BufferedInputStream(System.in);
             final ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            consumeWriteStream(consumer, bis, baos);
        }
    }

    public void consumeWriteStream(final SerializedAirbyteMessageConsumer consumer,
                                   final BufferedInputStream bis,
                                   final ByteArrayOutputStream baos)
            throws Exception {
        consumer.start();

        final byte[] buffer = new byte[8192]; // 8K buffer
        int bytesRead;
        boolean lastWasNewLine = false;

        while ((bytesRead = bis.read(buffer)) != -1) {
            for (int i = 0; i < bytesRead; i++) {
                final byte b = buffer[i];
                if (b == '\n' || b == '\r') {
                    if (!lastWasNewLine && baos.size() > 0) {
                        consumer.accept(baos.toString(StandardCharsets.UTF_8), baos.size());
                        baos.reset();
                    }
                    lastWasNewLine = true;
                } else {
                    baos.write(b);
                    lastWasNewLine = false;
                }
            }
        }

        // Handle last line if there's one
        if (baos.size() > 0) {
            consumer.accept(baos.toString(StandardCharsets.UTF_8), baos.size());
        }
    }
}
