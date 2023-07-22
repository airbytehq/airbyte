/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

public class NoopTyperDeduper implements TyperDeduper {

  @Override
  public void prepareFinalTables() throws Exception {

  }

  @Override
  public void typeAndDedupe(String originalNamespace, String originalName) throws Exception {

  }

  @Override
  public void commitFinalTables() throws Exception {

  }

}
