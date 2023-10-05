/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.util.Set;
import java.util.stream.Stream;

public record AlterTableReport(Set<String> columnsToAdd,
                               Set<String> columnsToRemove,
                               Set<String> columnsToChangeType,
                               boolean isDestinationV2Format) {

  /**
   * A no-op for an AlterTableReport is when the existing table matches the expected schema
   *
   * @return whether the schema matches
   */
  public boolean isNoOp() {
    return isDestinationV2Format && Stream.of(this.columnsToAdd, this.columnsToRemove, this.columnsToChangeType)
        .allMatch(Set::isEmpty);
  }

}
