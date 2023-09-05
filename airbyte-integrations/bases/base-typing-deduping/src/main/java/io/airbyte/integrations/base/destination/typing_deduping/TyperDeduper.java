/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

public interface TyperDeduper {

  void prepareTables() throws Exception;

  void typeAndDedupe(String originalNamespace, String originalName) throws Exception;

  void commitFinalTables() throws Exception;

}
