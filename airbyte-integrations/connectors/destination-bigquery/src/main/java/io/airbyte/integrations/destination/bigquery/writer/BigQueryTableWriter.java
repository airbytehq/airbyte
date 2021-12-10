package io.airbyte.integrations.destination.bigquery.writer;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.TableDataWriteChannel;
import com.google.common.base.Charsets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.gcs.writer.CommonWriter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.ByteBuffer;

public class BigQueryTableWriter implements CommonWriter {

    private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryTableWriter.class);

    private final TableDataWriteChannel writeChannel;

    public BigQueryTableWriter(TableDataWriteChannel writeChannel) {
        this.writeChannel = writeChannel;
    }

    @Override
    public void initialize() throws IOException { }

    @Override
    public void write(JsonNode formattedData) throws IOException {
        writeChannel.write(ByteBuffer.wrap((Jsons.serialize(formattedData) + "\n").getBytes(Charsets.UTF_8)));
    }

    @Override
    public void close(boolean hasFailed) throws Exception { this.writeChannel.close();  }

    public TableDataWriteChannel getWriteChannel() {
        return writeChannel;
    }
}
