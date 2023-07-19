/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package io.airbyte.integrations.destination.starrocks.io;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;

import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.Iterator;
import java.util.UUID;

import static io.airbyte.integrations.destination.starrocks.StarRocksConstants.CsvFormat;

public class StreamLoadStream extends InputStream {

    private static final int DEFAULT_BUFFER_SIZE = 2048;

    private final Iterator<AirbyteRecordMessage> recordIter;

    private ByteBuffer buffer;
    private byte[] cache;
    private int pos;
    private boolean endStream = false;

    public StreamLoadStream(Iterator<AirbyteRecordMessage> recordIter) {
        this.recordIter = recordIter;

        buffer = ByteBuffer.allocate(DEFAULT_BUFFER_SIZE);
        buffer.position(buffer.capacity());
    }


    @Override
    public int read() throws IOException {
        byte[] bytes = new byte[1];
        int ws = read(bytes);
        if (ws == -1) {
            return -1;
        }
        return bytes[0];
    }

    @Override
    public int read(byte[] b) throws IOException {
        return read(b, 0, b.length);
    }

    @Override
    public int read(byte[] b, int off, int len) throws IOException {
        if (len == 0) {
            return 0;
        }

        if (!buffer.hasRemaining()) {
            if (cache == null && endStream) {
                return -1;
            }
            fillBuffer();
        }

        int size = len - off;
        int ws = Math.min(size, buffer.remaining());
        buffer.get(b, off, ws);

        return ws;
    }

    @Override
    public void close() throws IOException {
        buffer = null;
        cache = null;
        pos = 0;
        endStream = true;
    }

    private void fillBuffer() {
        buffer.clear();
        if (cache != null) {
            writeBuffer(cache, pos);
        }

        if (endStream || !buffer.hasRemaining()) {
            buffer.flip();
            return;
        }

        byte[] bytes;
        while ((bytes = nextCsvRow()) != null) {
            writeBuffer(bytes, 0);
            bytes = null;
            if (!buffer.hasRemaining()) {
                break;
            }
        }
        if (buffer.position() == 0) {
            buffer.position(buffer.limit());
        } else {
            buffer.flip();
        }
    }

    private void writeBuffer(byte[] bytes, int pos) {
        int size = bytes.length - pos;

        int remain = buffer.remaining();

        int ws = Math.min(size, remain);
        buffer.put(bytes, pos, ws);
        if (size > remain) {
            this.cache = bytes;
            this.pos = pos + ws;
        } else {
            this.cache = null;
            this.pos = 0;
        }
    }


    private byte[] nextCsvRow() {
        if (recordIter.hasNext()) {
            AirbyteRecordMessage record = recordIter.next();
            return String.format(CsvFormat.LINE_PATTERN,
                    UUID.randomUUID(),
                    record.getEmittedAt(),
                Jsons.serialize(record.getData())).getBytes(StandardCharsets.UTF_8);
        } else {
            endStream = true;
            return CsvFormat.LINE_DELIMITER_BYTE;
        }
    }
}
