/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination.argproviders;

import static io.airbyte.integrations.standardtest.destination.argproviders.util.ArgumentProviderUtil.getProtocolVersion;

import io.airbyte.integrations.standardtest.destination.ProtocolVersion;
import java.util.stream.Stream;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DataTypeTestArgumentProvider implements ArgumentsProvider {

  private static final Logger LOGGER = LoggerFactory.getLogger(DataTypeTestArgumentProvider.class);

  public static final String INTEGER_TYPE_CATALOG = "data_type_integer_type_test_catalog.json";
  public static final String NUMBER_TYPE_CATALOG = "data_type_number_type_test_catalog.json";
  public static final String NAN_TYPE_MESSAGE = "nan_type_test_message.txt";
  public static final String INFINITY_TYPE_MESSAGE = "nan_type_test_message.txt";
  public static final CatalogMessageTestConfigWithCompatibility BASIC_TEST =
      new CatalogMessageTestConfigWithCompatibility("data_type_basic_test_catalog.json", "data_type_basic_test_messages.txt",
          new TestCompatibility(true, false, false));
  public static final CatalogMessageTestConfigWithCompatibility ARRAY_TEST =
      new CatalogMessageTestConfigWithCompatibility("data_type_array_test_catalog.json", "data_type_array_test_messages.txt",
          new TestCompatibility(true, true, false));
  public static final CatalogMessageTestConfigWithCompatibility OBJECT_TEST =
      new CatalogMessageTestConfigWithCompatibility("data_type_object_test_catalog.json", "data_type_object_test_messages.txt",
          new TestCompatibility(true, false, true));
  public static final CatalogMessageTestConfigWithCompatibility OBJECT_WITH_ARRAY_TEST =
      new CatalogMessageTestConfigWithCompatibility("data_type_array_object_test_catalog.json", "data_type_array_object_test_messages.txt",
          new TestCompatibility(true, true, true));
  private ProtocolVersion protocolVersion;

  @Override
  public Stream<? extends Arguments> provideArguments(ExtensionContext context) throws Exception {
    protocolVersion = getProtocolVersion(context);
    return Stream.of(
        getArguments(BASIC_TEST),
        getArguments(ARRAY_TEST),
        getArguments(OBJECT_TEST),
        getArguments(OBJECT_WITH_ARRAY_TEST));
  }

  private Arguments getArguments(CatalogMessageTestConfigWithCompatibility testConfig) {
    return Arguments.of(testConfig.getMessageFileVersion(protocolVersion), testConfig.getCatalogFileVersion(protocolVersion),
        testConfig.testCompatibility);
  }

  public record TestCompatibility(boolean requireBasicCompatibility,
                                  boolean requireArrayCompatibility,
                                  boolean requireObjectCompatibility) {

    public boolean isTestCompatible(boolean supportBasicDataTypeTest, boolean supportArrayDataTypeTest, boolean supportObjectDataTypeTest) {
      LOGGER.info("---- Data type test compatibility ----");
      LOGGER.info("| Data type test | Require | Support |");
      LOGGER.info("| Basic test     | {}   | {}   |", (requireBasicCompatibility ? "true " : "false"),
          (supportBasicDataTypeTest ? "true " : "false"));
      LOGGER.info("| Array test     | {}   | {}   |", (requireArrayCompatibility ? "true " : "false"),
          (supportArrayDataTypeTest ? "true " : "false"));
      LOGGER.info("| Object test    | {}   | {}   |", (requireObjectCompatibility ? "true " : "false"),
          (supportObjectDataTypeTest ? "true " : "false"));
      LOGGER.info("--------------------------------------");

      if (requireBasicCompatibility && !supportBasicDataTypeTest) {
        LOGGER.warn("The destination doesn't support required Basic data type test. The test is skipped!");
        return false;
      }
      if (requireArrayCompatibility && !supportArrayDataTypeTest) {
        LOGGER.warn("The destination doesn't support required Array data type test. The test is skipped!");
        return false;
      }
      if (requireObjectCompatibility && !supportObjectDataTypeTest) {
        LOGGER.warn("The destination doesn't support required Object data type test. The test is skipped!");
        return false;
      }

      return true;
    }

  }

  public static class CatalogMessageTestConfigWithCompatibility extends DataArgumentsProvider.CatalogMessageTestConfigPair {

    final TestCompatibility testCompatibility;

    public CatalogMessageTestConfigWithCompatibility(String catalogFile, String messageFile, TestCompatibility testCompatibility) {
      super(catalogFile, messageFile);
      this.testCompatibility = testCompatibility;
    }

  }

}
