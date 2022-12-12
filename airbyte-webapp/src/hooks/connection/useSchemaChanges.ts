import { useMemo } from "react";

import { SchemaChange } from "core/request/AirbyteClient";

import { useIsAutoDetectSchemaChangesEnabled } from "./useIsAutoDetectSchemaChangesEnabled";

export const useSchemaChanges = (schemaChange: SchemaChange) => {
  const isSchemaChangesEnabled = useIsAutoDetectSchemaChangesEnabled();

  return useMemo(() => {
    const hasSchemaChanges = isSchemaChangesEnabled && schemaChange !== SchemaChange.no_change;
    const hasBreakingSchemaChange = hasSchemaChanges && schemaChange === SchemaChange.breaking;
    const hasNonBreakingSchemaChange = hasSchemaChanges && schemaChange === SchemaChange.non_breaking;

    return {
      schemaChange,
      hasSchemaChanges,
      hasBreakingSchemaChange,
      hasNonBreakingSchemaChange,
    };
  }, [isSchemaChangesEnabled, schemaChange]);
};
