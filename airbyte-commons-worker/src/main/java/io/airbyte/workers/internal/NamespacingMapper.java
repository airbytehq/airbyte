/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
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
public class NamespacingMapper implements AirbyteMapper {

  private static final Logger LOGGER = LoggerFactory.getLogger(NamespacingMapper.class);

  private final NamespaceDefinitionType namespaceDefinition;
  private final String namespaceFormat;
  private final String streamPrefix;

  public NamespacingMapper(final NamespaceDefinitionType namespaceDefinition, final String namespaceFormat, final String streamPrefix) {
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
          final String namespace = formatNamespace(stream.getNamespace(), namespaceFormat);
          if (namespace == null) {
            LOGGER.error("Namespace Format cannot be blank for Stream {}. Falling back to default namespace from destination settings",
                stream.getName());
          }
          stream.withNamespace(namespace);
        }
      }
      stream.withName(transformStreamName(stream.getName(), streamPrefix));
    });
    return catalog;
  }

  @Override
  public AirbyteMessage mapMessage(final AirbyteMessage message) {
    if (message.getType() == Type.RECORD) {
      // Default behavior if namespaceDefinition is not set is to follow SOURCE
      if (namespaceDefinition != null) {
        if (namespaceDefinition.equals(NamespaceDefinitionType.DESTINATION)) {
          message.getRecord().withNamespace(null);
        } else if (namespaceDefinition.equals(NamespaceDefinitionType.CUSTOMFORMAT)) {
          message.getRecord().withNamespace(formatNamespace(message.getRecord().getNamespace(), namespaceFormat));
        }
      }
      message.getRecord().setStream(transformStreamName(message.getRecord().getStream(), streamPrefix));
      return message;
    }
    return message;
  }

  private static String formatNamespace(final String sourceNamespace, final String namespaceFormat) {
    String result = "";
    if (Strings.isNotBlank(namespaceFormat)) {
      final String regex = Pattern.quote("${SOURCE_NAMESPACE}");
      result = namespaceFormat.replaceAll(regex, Strings.isNotBlank(sourceNamespace) ? sourceNamespace : "");
    }
    if (Strings.isBlank(result)) {
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
