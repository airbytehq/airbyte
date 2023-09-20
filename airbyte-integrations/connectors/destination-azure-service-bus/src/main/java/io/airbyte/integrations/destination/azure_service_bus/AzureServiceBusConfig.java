/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_service_bus;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import com.google.common.base.Splitter;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Maps;
import io.airbyte.integrations.destination.azure_service_bus.auth.AzureConnectionString;
import java.util.Map;
import java.util.Optional;
import java.util.function.Supplier;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import lombok.Builder;
import lombok.Getter;
import lombok.NonNull;
import lombok.experimental.Accessors;
import lombok.extern.slf4j.Slf4j;
import okhttp3.HttpUrl;
import org.apache.commons.lang3.StringUtils;

@Slf4j
@Getter
@Builder(toBuilder = true)
@Accessors(chain = true)
public class AzureServiceBusConfig {

  static final String CONFIG_SERVICE_BUS_CONNECTION_STRING = "service_bus_connection_string";
  static final String CONFIG_QUEUE_NAME = "queue_name";
  static final String CONFIG_HEADER_MAP = "header_map";
  static final String CONFIG_ENDPOINT_URL_OVERRIDE = "endpoint_url";

  @NonNull
  private final String sharedAccessKeyName;
  @NonNull
  private final String sharedAccessKey;
  @NonNull
  private final String queueName;
  @NonNull
  private final HttpUrl endpointUrl;

  @NonNull
  private final Map<String, String> additionalHeaders;

  public static AzureServiceBusConfig fromJsonNode(final JsonNode configJsonNode) {
    AzureServiceBusConfigBuilder builder = AzureServiceBusConfig.builder();

    String connectRawStr = configJsonNode.path(CONFIG_SERVICE_BUS_CONNECTION_STRING).asText("");
    Preconditions.checkArgument(StringUtils.isNotBlank(connectRawStr),
        "required field %s is missing", CONFIG_SERVICE_BUS_CONNECTION_STRING);

    AzureConnectionString azConnectionString = new AzureConnectionString(connectRawStr);

    Preconditions.checkArgument(StringUtils.isNotBlank(azConnectionString.getSharedAccessKeyName()),
        "SharedAccessKeyName missing from connection string %s", connectRawStr);

    Preconditions.checkArgument(StringUtils.isNotBlank(azConnectionString.getSharedAccessKey()),
        "SharedAccessKey missing from connection string %s", connectRawStr);

    // determine queue name
    final String queueName = determineQueueName(azConnectionString, configJsonNode.path(CONFIG_QUEUE_NAME).asText())
        .orElseThrow(() -> new IllegalArgumentException("could not determine " + CONFIG_QUEUE_NAME));
    builder.queueName(queueName);

    HttpUrl.parse(azConnectionString.getEndpoint().toString());

    return builder
        .sharedAccessKeyName(azConnectionString.getSharedAccessKeyName())
        .additionalHeaders(parseHeaderMapConfig(configJsonNode.path(CONFIG_HEADER_MAP).asText()))
        .sharedAccessKey(azConnectionString.getSharedAccessKey())
        .endpointUrl(createEndpointUrl(configJsonNode, () -> azConnectionString.getEndpoint().getHost()))
        .build();
  }

  static HttpUrl createEndpointUrl(JsonNode configJsonNode, Supplier<String> hostNameFn) {
    if (!configJsonNode.path(CONFIG_ENDPOINT_URL_OVERRIDE).isMissingNode()) {
      String endpointUrl = configJsonNode.path(CONFIG_ENDPOINT_URL_OVERRIDE).asText("");
      log.debug("direct endpoint url supplied {}", endpointUrl);
      return HttpUrl.parse(endpointUrl)
          .newBuilder()
          .encodedPath("/").build();
    }

    return HttpUrl.parse("https://%s".formatted(hostNameFn.get()));
  }

  static Map<String, String> parseHeaderMapConfig(String headerMapConfigStr) {
    if (StringUtils.isBlank(headerMapConfigStr)) {
      return ImmutableMap.of();
    }
    Map<String, String> mapBuilder = Maps.newHashMap();
    final Pattern pattern = Pattern.compile("^(.+)=(.+)$");
    Splitter.on(";").trimResults().omitEmptyStrings()
        .splitToList(headerMapConfigStr)
        .forEach(keyValPair -> {
          Matcher matcher = pattern.matcher(keyValPair);
          Preconditions.checkArgument(matcher.find(), "%s does not confirm to key=val syntax", keyValPair);
          mapBuilder.put(matcher.group(1), matcher.group(2));
        });
    return ImmutableMap.copyOf(mapBuilder);
  }

  static Optional<String> determineQueueName(AzureConnectionString azConnectionString, String queueNameConfig) {
    if (StringUtils.isNotBlank(queueNameConfig)) {
      return Optional.of(queueNameConfig);
    }

    // fallback to entity path defined in connection string
    return Optional.ofNullable(azConnectionString.getEntityPath());
  }

}
