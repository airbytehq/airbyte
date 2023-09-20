/*
 * From Microsoft Corporation (MIT License).
 */

package io.airbyte.integrations.destination.azure_service_bus.auth;

import static java.nio.charset.StandardCharsets.UTF_8;

import com.google.common.base.Preconditions;
import io.micronaut.core.util.StringUtils;
import java.net.URLEncoder;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.time.Duration;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.temporal.ChronoUnit;
import java.util.Base64;
import java.util.Locale;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicReference;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import lombok.Getter;
import lombok.RequiredArgsConstructor;
import lombok.SneakyThrows;
import lombok.ToString;
import lombok.extern.slf4j.Slf4j;

/**
 * Authorizes with Azure Service Bus service using a shared access key from either a Service Bus namespace or a specific
 * Service Bus.
 *
 * <p>
 * The shared access key can be obtained by creating a <i>shared access policy</i> for the Service Bus namespace or for a
 * specific Service Bus instance. See <a href="https://docs.microsoft.com/en-us/azure/event-hubs/
 * authorize-access-shared-access-signature#shared-access-authorization-policies">Shared access authorization policies
 * </a> for more information.
 * </p>
 *
 * @see <a href="https://docs.microsoft.com/en-us/azure/event-hubs/authorize-access-shared-access-signature">Authorize
 * access with shared access signature.</a>
 */
@Slf4j
public class SharedAccessKeyGenerator {

  private static final String SHARED_ACCESS_SIGNATURE_FORMAT = "SharedAccessSignature sr=%s&sig=%s&se=%s&skn=%s";

  private final String policyName;
  private final Mac hmac;
  private final Duration tokenValidity = Duration.ofMinutes(40);

  private final AtomicReference<AccessToken> accessTokenRef = new AtomicReference<>();

  /**
   * Creates an instance that authorizes using the {@code policyName} and {@code sharedAccessKey}. The authorization lasts
   * for a period of {@code tokenValidity} before another token must be created.
   *
   * @param policyName Name of the shared access key policy.
   * @param sharedAccessKey Value of the shared access key.
   * @throws IllegalArgumentException if {@code policyName}, {@code sharedAccessKey} is an empty string. Or the duration of
   * {@code tokenValidity} is zero or a negative value. If the {@code sharedAccessKey} is an invalid value for the hashing
   * algorithm.
   * @throws NullPointerException if {@code policyName}, {@code sharedAccessKey}, or {@code tokenValidity} is null.
   * @throws UnsupportedOperationException If the hashing algorithm cannot be instantiated, which is used to generate the
   * shared access signatures.
   */
  public SharedAccessKeyGenerator(String policyName, String sharedAccessKey) {
    Objects.requireNonNull(sharedAccessKey, "'sharedAccessKey' cannot be null.");
    this.policyName = Objects.requireNonNull(policyName, "'policyName' cannot be null.");
    Preconditions.checkState(StringUtils.isNotEmpty(policyName), "policyName required");
    Preconditions.checkState(StringUtils.isNotEmpty(sharedAccessKey), "sharedAccessKey required");
    Preconditions.checkState(!tokenValidity.isZero() && !tokenValidity.isNegative(), "invalid validity");

    String hashStrategy = "HMACSHA256";
    try {
      hmac = Mac.getInstance(hashStrategy);
      final byte[] sasKeyBytes = sharedAccessKey.getBytes(UTF_8);
      final SecretKeySpec finalKey = new SecretKeySpec(sasKeyBytes, hashStrategy);
      hmac.init(finalKey);
    } catch (InvalidKeyException | NoSuchAlgorithmException e) {
      throw new UnsupportedOperationException(
          String.format("Unable to create hash mac for '%s'", hashStrategy), e);
    }
  }

  /**
   * Retrieves the token, given the audience/resources requested, for use in authorization against an Event Hubs namespace or
   * a specific Event Hub instance.
   */
  @SneakyThrows
  public AccessToken getToken(String queueUrl) {
    Preconditions.checkArgument(queueUrl != null && !queueUrl.isEmpty(), "queueUrl cannot be empty");

    AccessToken cachedToken = accessTokenRef.get();
    if (cachedToken != null && Instant.now().isBefore(cachedToken.getExpiresAt().toInstant())) {
      log.debug("returning cached token");
      return cachedToken;
    }

    final String utf8Encoding = UTF_8.name();
    final OffsetDateTime expiresOn = OffsetDateTime.now(ZoneOffset.UTC).plus(tokenValidity);
    final String expiresOnEpochSeconds = Long.toString(expiresOn.toEpochSecond());
    final String audienceUri = URLEncoder.encode(queueUrl, utf8Encoding);
    final String secretToSign = audienceUri + "\n" + expiresOnEpochSeconds;

    final byte[] signatureBytes = hmac.doFinal(secretToSign.getBytes(utf8Encoding));
    final String signature = Base64.getEncoder().encodeToString(signatureBytes);

    final String token = String.format(Locale.US, SHARED_ACCESS_SIGNATURE_FORMAT,
        audienceUri,
        URLEncoder.encode(signature, utf8Encoding),
        URLEncoder.encode(expiresOnEpochSeconds, utf8Encoding),
        URLEncoder.encode(policyName, utf8Encoding));

    // inform our system that it expires 2 minutes prior to hard expiry that was signed
    final AccessToken accessToken = new AccessToken(token, expiresOn.minus(2, ChronoUnit.MINUTES));
    accessTokenRef.set(accessToken);

    return accessToken;
  }

  void invalidateTokenCache() {
    accessTokenRef.set(null);
  }

  @Getter
  @RequiredArgsConstructor
  @ToString
  public static class AccessToken {

    private final String token;
    private final OffsetDateTime expiresAt;
  }
}
