package io.airbyte.integrations.source.mysql;/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

import static org.junit.jupiter.api.Assertions.*;

import com.github.zafarkhaja.semver.Version;
import io.airbyte.cdk.CDKConstants;
import org.junit.jupiter.api.Test;

class CDKVersionTest {

  /**
   * This test ensures that the CDK version number matches a valid semantic versioning (SemVer)
   * format.
   *
   * If the CDK version number includes a '-SNAPSHOT' suffix, this is removed before testing.
   *
   * Fails if the CDK version number does not match a valid SemVer format.
   */
  @Test
  void cdkVersionShouldMatchSemVer() {
    String cdkVersion = CDKConstants.VERSION.replace("-SNAPSHOT", "");
    assertDoesNotThrow(() -> Version.valueOf(cdkVersion));
  }

}
