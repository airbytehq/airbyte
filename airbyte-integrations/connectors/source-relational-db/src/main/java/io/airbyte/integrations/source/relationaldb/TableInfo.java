/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import java.util.List;
import lombok.Builder;
import lombok.Getter;

/**
 * This class encapsulates all externally relevant Table information.
 */
@Getter
@Builder
public class TableInfo<T> {

  private final String nameSpace;
  private final String name;
  private final List<T> fields;
  private final List<String> primaryKeys;
  private final List<String> cursorFields;

}
