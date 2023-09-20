package io.airbyte.integrations.destination.azure_service_bus.auth;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import org.junit.jupiter.api.Test;

public class AzureConnectionStringTest {

  @Test
  void branchTest() {
    assertThatThrownBy(() -> new AzureConnectionString("Endpoint=sb://foo.servicebus.windows.net/;UnknownKey=foo"))
        .hasMessageContaining("UnknownKey");
    assertThatThrownBy(() -> new AzureConnectionString(""))
        .hasMessageContaining("empty string");
    assertThatThrownBy(() -> new AzureConnectionString("Endpoint=sb:////something^odd::42/"))
        .hasMessageContaining("Invalid endpoint");
    assertThatThrownBy(() -> new AzureConnectionString("Endpoint=;SharedAccessKeyName=someKeyName"))
        .hasMessageContaining("'Endpoint'");

  }

  @Test
  void getEndpoint() {
    assertThat(getVanillaConnect().getEndpoint().getHost())
        .isEqualTo("foo.servicebus.windows.net");
    assertThat(new AzureConnectionString(
        "Endpoint=foo.servicebus.windows.net/;SharedAccessKeyName=someKeyName;SharedAccessKey=someKeyValue")
        .getEndpoint().getHost())
        .isEqualTo("foo.servicebus.windows.net");
  }

  @Test
  void getEntityPath() {
    assertThat(getVanillaConnect().getEntityPath())
        .isEqualTo("bar-queue-name");
  }

  @Test
  void getSharedAccessKeyName() {
    assertThat(getVanillaConnect().getSharedAccessKey())
        .isEqualTo("someKeyValue");
  }

  @Test
  void getSharedAccessKey() {
    assertThat(getVanillaConnect().getSharedAccessKeyName())
        .isEqualTo("someKeyName");
  }

  public static AzureConnectionString getVanillaConnect() {
    return new AzureConnectionString("Endpoint=sb://foo.servicebus.windows.net/"
        + ";SharedAccessKeyName=someKeyName;SharedAccessKey=someKeyValue;EntityPath=bar-queue-name");
  }

}