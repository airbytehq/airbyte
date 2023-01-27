/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oracle_strict_encrypt;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.base.ssh.SshHelpers;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class OracleStrictEncryptDestinationTest {

  @Test
  void testGetSpec() throws Exception {
    var expected = SshHelpers.injectSshIntoSpec(
        Jsons.deserialize(MoreResources.readResource("expected_spec.json"), ConnectorSpecification.class));
    var actual = new OracleStrictEncryptDestination().spec();
    Assertions.assertEquals(expected, actual);
  }

}
