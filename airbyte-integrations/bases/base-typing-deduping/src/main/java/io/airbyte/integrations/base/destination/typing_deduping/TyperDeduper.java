/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.math.BigInteger;

public interface TyperDeduper {

  void prepareTables() throws Exception;

  void typeAndDedupe(String originalNamespace, String originalName, final BigInteger limit) throws Exception;

  void commitFinalTables() throws Exception;

}
