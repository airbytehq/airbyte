import { useMemo } from "react";

import { SchemaChange } from "core/request/AirbyteClient";

export const useSchemaChanges = (schemaChange: SchemaChange) => {
  const isSchemaChangesFeatureEnabled = process.env.REACT_APP_AUTO_DETECT_SCHEMA_CHANGES === "true";

  return useMemo(() => {
    const hasSchemaChanges = isSchemaChangesFeatureEnabled && schemaChange !== SchemaChange.no_change;
    const hasBreakingSchemaChange = hasSchemaChanges && schemaChange === SchemaChange.breaking;
    const hasNonBreakingSchemaChange = hasSchemaChanges && schemaChange === SchemaChange.non_breaking;

    return {
      schemaChange,
      hasSchemaChanges,
      hasBreakingSchemaChange,
      hasNonBreakingSchemaChange,
    };
  }, [isSchemaChangesFeatureEnabled, schemaChange]);
};
