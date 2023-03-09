/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.errors;

import io.airbyte.commons.version.Version;

public class UnsupportedProtocolVersionException extends KnownException {

  public UnsupportedProtocolVersionException(final Version current, final Version minSupported, final Version maxSupported) {
    this(current.serialize(), minSupported, maxSupported);
  }

  public UnsupportedProtocolVersionException(final String current, final Version minSupported, final Version maxSupported) {
    super(String.format("Airbyte Protocol Version %s is not supported. (Must be within [%s:%s])",
        current, minSupported.serialize(), maxSupported.serialize()));
  }

  @Override
  public int getHttpCode() {
    return 400;
  }

}
