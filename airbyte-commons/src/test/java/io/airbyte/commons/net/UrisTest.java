/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.net;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.Optional;
import org.junit.jupiter.api.Test;

class UrisTest {

  @Test
  void testFromStringOrNull() throws URISyntaxException {
    assertEquals(Optional.empty(), Uris.fromStringOrNull(null));
    assertEquals(Optional.of(new URI("hello.com")), Uris.fromStringOrNull("hello.com"));
  }

}
