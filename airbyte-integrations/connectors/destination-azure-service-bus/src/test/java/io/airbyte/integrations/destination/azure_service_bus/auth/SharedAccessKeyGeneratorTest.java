package io.airbyte.integrations.destination.azure_service_bus.auth;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import io.airbyte.integrations.destination.azure_service_bus.auth.SharedAccessKeyGenerator.AccessToken;
import java.time.OffsetDateTime;
import java.time.ZonedDateTime;
import java.util.stream.Stream;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

class SharedAccessKeyGeneratorTest {

  @ParameterizedTest
  @MethodSource("getSas")
  public void testSharedAccessSignatureCredential(String sas, OffsetDateTime expectedExpirationTime) {
    SharedAccessKeyGenerator serviceBusSharedKeyCredential = new SharedAccessKeyGenerator("test-sas-key", sas);
    AccessToken token = serviceBusSharedKeyCredential.getToken("https://entity-name" + getEndpoint() + "/");
    assertNotNull(token.getToken());
    assertThat(token.getExpiresAt())
        .isAfter(ZonedDateTime.now().toOffsetDateTime());
    assertThat(token.getToken())
        .contains("entity-name");
    assertThat(token.getToken())
        .contains("test-sas-key");

    assertThat(token)
        .as("get cache")
        .isEqualTo(serviceBusSharedKeyCredential.getToken("https://entity-name" + getEndpoint() + "/"));

    serviceBusSharedKeyCredential.invalidateTokenCache();
  }

  private static Stream<Arguments> getSas() {
    String validSas = "SharedAccessSignature "
        + "sr=https%3A%2F%2Fentity-name" + getEndpoint() + "%2F"
        + "&sig=encodedsignature%3D"
        + "&se=1599537084"
        + "&skn=test-sas-key";
    String validSasWithNoExpirationTime = "SharedAccessSignature "
        + "sr=https%3A%2F%2Fentity-name" + getEndpoint() + "%2F"
        + "&sig=encodedsignature%3D"
        + "&skn=test-sas-key";
    String validSasInvalidExpirationTimeFormat = "SharedAccessSignature "
        + "sr=https%3A%2F%2Fentity-name" + getEndpoint() + "%2F"
        + "&sig=encodedsignature%3D"
        + "&se=se=2020-12-31T13:37:45Z"
        + "&skn=test-sas-key";

    return Stream.of(
        Arguments.of(validSas, OffsetDateTime.parse("2020-09-08T03:51:24Z")),
        Arguments.of(validSasWithNoExpirationTime, OffsetDateTime.MAX),
        Arguments.of(validSasInvalidExpirationTimeFormat, OffsetDateTime.MAX)
    );
  }

  private static String getEndpoint() {
    return ".servicebus.windows.net";
  }


}