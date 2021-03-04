/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.workers.protocols.airbyte;

import com.google.common.base.Preconditions;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardTargetConfig;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.workers.WorkerException;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * We apply some transformations on the fly on the catalog (same should be done on records too) from
 * the source before it reaches the destination. One of the transformation is to define the
 * destination namespace where data will be stored and how to mirror (or not) the namespace used in
 * the source (if any). This is configured in the UI through the syncInput.
 */
public class DefaultAirbyteMapper implements AirbyteMapper {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultAirbyteMapper.class);

  private StandardSyncInput syncInput;

  public DefaultAirbyteMapper() {}

  @Override
  public void start(StandardTargetConfig targetConfig, StandardSyncInput syncInput) throws IOException, WorkerException {
    this.syncInput = syncInput;
    transformConfiguredCatalog(targetConfig.getCatalog(), syncInput);
  }

  @Override
  public void accept(AirbyteMessage message) throws IOException {
    Preconditions.checkState(syncInput != null);

    if (message.getCatalog() != null) {
      transformCatalog(message.getCatalog(), syncInput);
    }
    message.getRecord().setStream(transformStreamName(message.getRecord().getStream(), syncInput));
  }

  @Override
  public void close() throws Exception {}

  private static void transformConfiguredCatalog(ConfiguredAirbyteCatalog catalog, StandardSyncInput syncInput) {
    catalog.getStreams().forEach(s -> transformStream(s.getStream(), syncInput));
  }

  private static void transformCatalog(AirbyteCatalog catalog, StandardSyncInput syncInput) {
    catalog.getStreams().forEach(s -> transformStream(s, syncInput));
  }

  private static AirbyteStream transformStream(AirbyteStream stream, StandardSyncInput syncInput) {
    return stream.withName(transformStreamName(stream.getName(), syncInput));
  }

  private static String transformStreamName(String streamName, StandardSyncInput syncInput) {
    // Use the connection name as a prefix for the moment to alter the stream name in the destination
    return syncInput.getNamespaceDefault() + "_" + streamName;
  }

}
