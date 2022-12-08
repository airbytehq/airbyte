import { useMemo } from "react";

import { SchemaChange } from "core/request/AirbyteClient";
import { FeatureItem, useFeature } from "hooks/services/Feature";

export const useSchemaChanges = (schemaChange: SchemaChange) => {
  const allowAutoDetectSchemaChanges = useFeature(FeatureItem.AllowAutoDetectSchemaChanges);

  return useMemo(() => {
    const hasSchemaChanges = allowAutoDetectSchemaChanges && schemaChange !== SchemaChange.no_change;
    const hasBreakingSchemaChange = hasSchemaChanges && schemaChange === SchemaChange.breaking;
    const hasNonBreakingSchemaChange = hasSchemaChanges && schemaChange === SchemaChange.non_breaking;

    return {
      schemaChange,
      hasSchemaChanges,
      hasBreakingSchemaChange,
      hasNonBreakingSchemaChange,
    };
  }, [allowAutoDetectSchemaChanges, schemaChange]);
};
