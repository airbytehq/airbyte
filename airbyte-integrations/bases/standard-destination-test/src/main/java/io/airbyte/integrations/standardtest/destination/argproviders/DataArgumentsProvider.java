/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination.argproviders;

import static io.airbyte.integrations.standardtest.destination.argproviders.util.ArgumentProviderUtil.getProtocolVersion;
import static io.airbyte.integrations.standardtest.destination.argproviders.util.ArgumentProviderUtil.prefixFileNameByVersion;

import io.airbyte.integrations.standardtest.destination.ProtocolVersion;
import java.util.stream.Stream;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;

/**
 * Class encapsulating all arguments required for Standard Destination Tests.
 *
 * All files defined here can be found in src/main/resources of this package.
 */
public class DataArgumentsProvider implements ArgumentsProvider {

  public static final CatalogMessageTestConfigPair EXCHANGE_RATE_CONFIG =
      new CatalogMessageTestConfigPair("exchange_rate_catalog.json", "exchange_rate_messages.txt");
  public static final CatalogMessageTestConfigPair EDGE_CASE_CONFIG =
      new CatalogMessageTestConfigPair("edge_case_catalog.json", "edge_case_messages.txt");
  public static final CatalogMessageTestConfigPair NAMESPACE_CONFIG =
      new CatalogMessageTestConfigPair("namespace_catalog.json", "namespace_messages.txt");

  @Override
  public Stream<? extends Arguments> provideArguments(final ExtensionContext context) throws Exception {
    ProtocolVersion protocolVersion = getProtocolVersion(context);
    return Stream.of(
        Arguments.of(EXCHANGE_RATE_CONFIG.getMessageFileVersion(protocolVersion), EXCHANGE_RATE_CONFIG.getCatalogFileVersion(protocolVersion)),
        Arguments.of(EDGE_CASE_CONFIG.getMessageFileVersion(protocolVersion), EDGE_CASE_CONFIG.getCatalogFileVersion(protocolVersion))
    // todo - need to use the new protocol to capture this.
    // Arguments.of("stripe_messages.txt", "stripe_schema.json")
    );

  }

  public static class CatalogMessageTestConfigPair {

    final String catalogFile;
    final String messageFile;

    public CatalogMessageTestConfigPair(final String catalogFile, final String messageFile) {
      this.catalogFile = catalogFile;
      this.messageFile = messageFile;
    }

    public String getCatalogFileVersion(ProtocolVersion protocolVersion) {
      return prefixFileNameByVersion(catalogFile, protocolVersion);
    }

    public String getMessageFileVersion(ProtocolVersion protocolVersion) {
      return prefixFileNameByVersion(messageFile, protocolVersion);
    }

  }

}
