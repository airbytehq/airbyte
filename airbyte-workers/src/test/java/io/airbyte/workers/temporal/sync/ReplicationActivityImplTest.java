package io.airbyte.workers.temporal.sync;


import org.junit.jupiter.api.Test;

import java.util.concurrent.atomic.AtomicReference;

import static org.junit.jupiter.api.Assertions.assertEquals;


class ReplicationActivityImplTest {
    @Test
    public void testLogTransform() {
        final String original = "2021-12-08 17:18:10 ERROR i.a.c.i.LineGobbler(voidCall):82 - {log_source=\u001b[43mdestination\u001B[0m, workspace_app_root=/tmp/workspace/scheduler/logs} - WARNING: The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8";
        final String expected = "\u001b[43mdestination\u001B[0m 2021-12-08 17:18:10 ERROR i.a.c.i.LineGobbler(voidCall):82 - {workspace_app_root=/tmp/workspace/scheduler/logs} - WARNING: The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8";

        final AtomicReference<String> actualReference = new AtomicReference<>();
        ReplicationActivityImpl.prefixMovingLogger(actualReference::set, original);
        final String actual = actualReference.get();

        assertEquals(expected, actual);
    }

}