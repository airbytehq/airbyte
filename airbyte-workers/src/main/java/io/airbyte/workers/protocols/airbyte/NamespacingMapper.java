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

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.workers.protocols.Mapper;

/**
 * We apply some transformations on the fly on the catalog (same should be done on records too) from
 * the source before it reaches the destination. One of the transformation is to define the
 * destination namespace where data will be stored and how to mirror (or not) the namespace used in
 * the source (if any). This is configured in the UI through the syncInput.
 */
public class NamespacingMapper implements Mapper<AirbyteMessage> {

  private final String defaultNamespace;

  public NamespacingMapper(String defaultNamespace) {
    this.defaultNamespace = defaultNamespace;
  }

  @Override
  public ConfiguredAirbyteCatalog mapCatalog(final ConfiguredAirbyteCatalog inputCatalog) {
    final ConfiguredAirbyteCatalog catalog = Jsons.clone(inputCatalog);
    catalog.getStreams().forEach(s -> mutateStream(s.getStream(), defaultNamespace));
    return catalog;
  }

  @Override
  public AirbyteMessage mapMessage(final AirbyteMessage inputMessage) {
    if (inputMessage.getType() == Type.RECORD) {
      final AirbyteMessage message = Jsons.clone(inputMessage);
      message.getRecord().setStream(transformStreamName(message.getRecord().getStream(), defaultNamespace));
      return message;
    }
    return inputMessage;
  }

  private static void mutateStream(final AirbyteStream stream, final String defaultNamespace) {
    stream.withName(transformStreamName(stream.getName(), defaultNamespace));
  }

  private static String transformStreamName(final String streamName, final String defaultNamespace) {
    // Use the default namespace as a prefix for the moment to alter the stream name in the destination
    if (defaultNamespace != null && !defaultNamespace.isEmpty()) {
      // TODO chris: use defaultNamespace as a namespace/schema/dataset in destination
      return defaultNamespace + "_" + streamName;
    } else {
      // TODO chris: check to make sure that source is providing a namespace, otherwise this should not be
      // allowed (requires PR #2228)
      // throw new RuntimeException(String.format("Destination Namespace is not defined for %s",
      // streamName));
      // For now, since destination still defines a default namespace in their settings, thus it's
      // acceptable not having one so we can keep the stream name as is.
      return streamName;
    }
  }

}
