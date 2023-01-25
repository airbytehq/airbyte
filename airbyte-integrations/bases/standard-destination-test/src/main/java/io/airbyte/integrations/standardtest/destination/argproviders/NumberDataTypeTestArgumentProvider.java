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

public class NumberDataTypeTestArgumentProvider implements ArgumentsProvider {

  public static final String NUMBER_DATA_TYPE_TEST_CATALOG = "number_data_type_test_catalog.json";
  public static final String NUMBER_DATA_TYPE_TEST_MESSAGES = "number_data_type_test_messages.txt";
  public static final String NUMBER_DATA_TYPE_ARRAY_TEST_CATALOG = "number_data_type_array_test_catalog.json";
  public static final String NUMBER_DATA_TYPE_ARRAY_TEST_MESSAGES = "number_data_type_array_test_messages.txt";
  private ProtocolVersion protocolVersion;

  @Override
  public Stream<? extends Arguments> provideArguments(ExtensionContext context) throws Exception {
    protocolVersion = getProtocolVersion(context);
    return Stream.of(
        getArguments(NUMBER_DATA_TYPE_TEST_CATALOG, NUMBER_DATA_TYPE_TEST_MESSAGES),
        getArguments(NUMBER_DATA_TYPE_ARRAY_TEST_CATALOG, NUMBER_DATA_TYPE_ARRAY_TEST_MESSAGES));
  }

  private Arguments getArguments(final String catalogFile, final String messageFile) {
    return Arguments.of(prefixFileNameByVersion(catalogFile, protocolVersion), prefixFileNameByVersion(messageFile, protocolVersion));
  }

}
