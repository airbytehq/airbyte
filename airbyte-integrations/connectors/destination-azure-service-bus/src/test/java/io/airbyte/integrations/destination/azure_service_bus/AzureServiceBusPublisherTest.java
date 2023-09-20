package io.airbyte.integrations.destination.azure_service_bus;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;

import java.util.List;
import org.junit.jupiter.api.Test;

class AzureServiceBusPublisherTest {

  @Test
  void serializePrimaryKeyStruct() {
    assertThat(AzureServiceBusPublisher.serializePrimaryKeyStruct(null))
        .as("handle null")
        .isEqualTo("");

    assertThat(AzureServiceBusPublisher.serializePrimaryKeyStruct(List.of(List.of())))
        .as("handle empty lists")
        .isEqualTo("");

    assertThat(AzureServiceBusPublisher.serializePrimaryKeyStruct(List.of(List.of("SOME_ID"))))
        .as("typical struct")
        .isEqualTo("SOME_ID");
  }

  @Test
  void serializePrimaryKeyStruct_complex() {
    List<List<String>> primaryKeyStruct = List.of(
        List.of("ID_3"),
        List.of("SOME_ID", "ID2"));
    assertThat(AzureServiceBusPublisher.serializePrimaryKeyStruct(primaryKeyStruct))
        .as("complex struct serialized to compatible char set to service bus headers")
        .isEqualTo("ID_3;SOME_ID,ID2");
  }
}