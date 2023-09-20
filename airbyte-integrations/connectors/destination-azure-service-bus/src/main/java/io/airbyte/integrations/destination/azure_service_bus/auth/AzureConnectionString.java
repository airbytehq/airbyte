/*
 * From Microsoft Corporation (MIT License).
 */

package io.airbyte.integrations.destination.azure_service_bus.auth;

import com.google.common.base.Preconditions;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Locale;
import java.util.Objects;
import lombok.Getter;

/**
 * The set of properties that comprise a connection string from the Azure portal.
 */
@Getter
public class AzureConnectionString {

  /**
   * The endpoint address, including protocol, from the connection string.
   */
  private final URI endpoint;

  /**
   * The entity path to connect to in the message broker.
   */
  private final String entityPath;

  private final String sharedAccessKeyName;
  private final String sharedAccessKey;

  /**
   * Creates a new instance by parsing the {@code connectionString} into its components.
   *
   * @param connectionString The connection string to the Event Hub instance.
   * @throws NullPointerException if {@code connectionString} is null.
   * @throws IllegalArgumentException if {@code connectionString} is an empty string or the connection string has an invalid
   * format.
   */
  public AzureConnectionString(String connectionString) {
    Objects.requireNonNull(connectionString, "'connectionString' cannot be null.");
    Preconditions.checkArgument(!connectionString.isEmpty(), "'connectionString' cannot be an empty string.");

    final String[] tokenValuePairs = connectionString.split(";");
    URI endpoint = null;
    String entityPath = null;
    String sharedAccessKeyName = null;
    String sharedAccessKeyValue = null;

    for (String tokenValuePair : tokenValuePairs) {
      final String[] pair = tokenValuePair.split("=", 2);
      Preconditions.checkArgument(pair.length == 2,
          String.format(Locale.US, "Connection string has invalid key value pair: %s", tokenValuePair));

      final String key = pair[0].trim();
      final String value = pair[1].trim();

      if (key.equalsIgnoreCase("Endpoint")) {
        final String endpointUri = validateAndUpdateDefaultScheme(value);
        try {
          endpoint = new URI(endpointUri);
        } catch (URISyntaxException e) {
          throw new IllegalArgumentException(
              String.format(Locale.US, "Invalid endpoint: %s", tokenValuePair), e);
        }
      } else if (key.equalsIgnoreCase("SharedAccessKeyName")) {
        sharedAccessKeyName = value;
      } else if (key.equalsIgnoreCase("SharedAccessKey")) {
        sharedAccessKeyValue = value;
      } else if (key.equalsIgnoreCase("EntityPath")) {
        entityPath = value;
      } else {
        throw new IllegalArgumentException(
            String.format(Locale.US, "Illegal connection string parameter name: %s", key));
      }
    }

    // connection string should have an endpoint and either shared access signature or shared access key and value
    boolean hasSharedKeyAndValue = sharedAccessKeyName != null && sharedAccessKeyValue != null;
    // invalid key, value and SAS
    Preconditions.checkArgument(endpoint != null && hasSharedKeyAndValue, "Could not parse 'connectionString'");

    this.endpoint = endpoint;
    this.entityPath = entityPath;
    this.sharedAccessKeyName = sharedAccessKeyName;
    this.sharedAccessKey = sharedAccessKeyValue;
  }

  /*
   * The function checks for pre-existing scheme of "sb://" , "http://" or "https://". If the scheme is not provided
   * in endpoint, it will set the default scheme to "sb://".
   */
  private String validateAndUpdateDefaultScheme(final String endpoint) {
    Preconditions.checkArgument(endpoint != null && !endpoint.isEmpty(),
        "'Endpoint' must be provided in 'connectionString'.");

    final String endpointLowerCase = endpoint.trim().toLowerCase(Locale.ROOT);
    if (!endpointLowerCase.startsWith("sb://") && !endpointLowerCase.startsWith("https://")) {
      return "sb://" + endpoint;
    }
    return endpointLowerCase;
  }

}
