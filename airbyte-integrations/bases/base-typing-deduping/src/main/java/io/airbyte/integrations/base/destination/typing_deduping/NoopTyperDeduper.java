/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.math.BigInteger;

public class NoopTyperDeduper implements TyperDeduper {

  @Override
  public void prepareTables() throws Exception {

  }

  @Override
  public void typeAndDedupe(String originalNamespace, String originalName, final BigInteger limit) throws Exception {

  }

  @Override
  public void commitFinalTables() throws Exception {

  }

}
