import { useMemo } from "react";

import { SchemaChange } from "core/request/AirbyteClient";
import { FeatureItem, useFeature } from "hooks/services/Feature";

export const useSchemaChanges = (schemaChange: SchemaChange) => {
  const allowAutoDetectSchema = useFeature(FeatureItem.AllowAutoDetectSchema);

  return useMemo(() => {
    const hasSchemaChanges = allowAutoDetectSchema && schemaChange !== SchemaChange.no_change;
    const hasBreakingSchemaChange = hasSchemaChanges && schemaChange === SchemaChange.breaking;
    const hasNonBreakingSchemaChange = hasSchemaChanges && schemaChange === SchemaChange.non_breaking;

    return {
      schemaChange,
      hasSchemaChanges,
      hasBreakingSchemaChange,
      hasNonBreakingSchemaChange,
    };
  }, [allowAutoDetectSchema, schemaChange]);
};
