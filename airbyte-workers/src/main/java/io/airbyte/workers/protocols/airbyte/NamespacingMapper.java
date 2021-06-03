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
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.workers.protocols.Mapper;
import java.util.regex.Pattern;
import org.apache.logging.log4j.util.Strings;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * We apply some transformations on the fly on the catalog (same should be done on records too) from
 * the source before it reaches the destination. One of the transformation is to define the
 * destination namespace where data will be stored and how to mirror (or not) the namespace used in
 * the source (if any). This is configured in the UI through the syncInput.
 */
public class NamespacingMapper implements Mapper<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(NamespacingMapper.class);

  private final NamespaceDefinitionType namespaceDefinition;
  private final String namespaceFormat;
  private final String streamPrefix;

  public NamespacingMapper(NamespaceDefinitionType namespaceDefinition, String namespaceFormat, String streamPrefix) {
    this.namespaceDefinition = namespaceDefinition;
    this.namespaceFormat = namespaceFormat;
    this.streamPrefix = streamPrefix;
  }

  @Override
  public ConfiguredAirbyteCatalog mapCatalog(final ConfiguredAirbyteCatalog inputCatalog) {
    final ConfiguredAirbyteCatalog catalog = Jsons.clone(inputCatalog);
    catalog.getStreams().forEach(s -> {
      final AirbyteStream stream = s.getStream();
      // Default behavior if namespaceDefinition is not set is to follow SOURCE
      if (namespaceDefinition != null) {
        if (namespaceDefinition.equals(NamespaceDefinitionType.DESTINATION)) {
          stream.withNamespace(null);
        } else if (namespaceDefinition.equals(NamespaceDefinitionType.CUSTOMFORMAT)) {
          stream.withNamespace(formatNamespace(stream.getName(), stream.getNamespace(), namespaceFormat));
        }
      }
      stream.withName(transformStreamName(stream.getName(), streamPrefix));
    });
    return catalog;
  }

  @Override
  public AirbyteMessage mapMessage(final AirbyteMessage inputMessage) {
    if (inputMessage.getType() == Type.RECORD) {
      final AirbyteMessage message = Jsons.clone(inputMessage);
      // Default behavior if namespaceDefinition is not set is to follow SOURCE
      if (namespaceDefinition != null) {
        if (namespaceDefinition.equals(NamespaceDefinitionType.DESTINATION)) {
          message.getRecord().withNamespace(null);
        } else if (namespaceDefinition.equals(NamespaceDefinitionType.CUSTOMFORMAT)) {
          message.getRecord().withNamespace(formatNamespace(message.getRecord().getStream(), message.getRecord().getNamespace(), namespaceFormat));
        }
      }
      message.getRecord().setStream(transformStreamName(message.getRecord().getStream(), streamPrefix));
      return message;
    }
    return inputMessage;
  }

  private static String formatNamespace(String streamName, final String sourceNamespace, final String namespaceFormat) {
    String result = "";
    if (Strings.isNotBlank(namespaceFormat)) {
      final String regex = Pattern.quote("${SOURCE_NAMESPACE}");
      result = namespaceFormat.replaceAll(regex, Strings.isNotEmpty(sourceNamespace) ? sourceNamespace : "");
    }
    if (Strings.isBlank(result)) {
      LOGGER.error("Namespace Format cannot be blank for Stream {}. Falling back to default namespace from destination settings", streamName);
      result = null;
    }
    return result;
  }

  private static String transformStreamName(final String streamName, final String prefix) {
    if (Strings.isNotBlank(prefix)) {
      return prefix + streamName;
    } else {
      return streamName;
    }
  }

}
