/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.net;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.Optional;
import javax.annotation.Nullable;

public class Uris {

  /**
   * Helper to handle nulls when creating a URI from a string. If null, then empty optional.
   * Otherwise, URI of the string.
   *
   * @param stringOrNull - string to convert into a URI. can be null.
   * @return optional URI of the string or empty optional if input is null.
   */
  public static Optional<URI> fromStringOrNull(@Nullable final String stringOrNull) throws URISyntaxException {
    if (stringOrNull == null) {
      return Optional.empty();
    } else {
      return Optional.of(new URI(stringOrNull));
    }
  }

}
