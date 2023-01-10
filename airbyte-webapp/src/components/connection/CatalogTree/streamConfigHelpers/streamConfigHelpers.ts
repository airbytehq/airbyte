import isEqual from "lodash/isEqual";

import { AirbyteStreamConfiguration, SelectedFieldInfo } from "core/request/AirbyteClient";

/**
 * Merges arrays of SelectedFieldInfo, ensuring there are no duplicates
 */
export function mergeFieldPathArrays(...args: SelectedFieldInfo[][]): SelectedFieldInfo[] {
  const set = new Set<string>();

  args.forEach((array) =>
    array.forEach((selectedFieldInfo) => {
      if (selectedFieldInfo.fieldPath) {
        const key = JSON.stringify(selectedFieldInfo.fieldPath);
        set.add(key);
      }
    })
  );

  return Array.from(set).map((key) => ({ fieldPath: JSON.parse(key) }));
}

/**
 * Updates the cursor field in AirbyteStreamConfiguration
 */
export const updateCursorField = (
  config: AirbyteStreamConfiguration,
  selectedCursorField: string[],
  numberOfFieldsInStream: number
): Partial<AirbyteStreamConfiguration> => {
  // If field selection is enabled, we need to be sure the new cursor is also selected
  if (config?.fieldSelectionEnabled) {
    const previouslySelectedFields = config?.selectedFields || [];
    const selectedFields = mergeFieldPathArrays(previouslySelectedFields, [{ fieldPath: selectedCursorField }]);

    // If the number of selected fields is equal to the fields in the stream, field selection is disabled because all fields are selected
    if (selectedFields.length === numberOfFieldsInStream) {
      return { cursorField: selectedCursorField, selectedFields: [], fieldSelectionEnabled: false };
    }

    return {
      fieldSelectionEnabled: true,
      selectedFields,
      cursorField: selectedCursorField,
    };
  }
  return { cursorField: selectedCursorField };
};

/**
 * Overwrites the entire primaryKey value in AirbyteStreamConfiguration, which is a composite of one or more fieldPaths
 */
export const updatePrimaryKey = (
  config: AirbyteStreamConfiguration,
  compositePrimaryKey: string[][],
  numberOfFieldsInStream: number
): Partial<AirbyteStreamConfiguration> => {
  // If field selection is enabled, we need to be sure each fieldPath in the new composite primary key is also selected
  if (config?.fieldSelectionEnabled) {
    const previouslySelectedFields = config?.selectedFields || [];
    const selectedFields = mergeFieldPathArrays(
      previouslySelectedFields,
      compositePrimaryKey.map((fieldPath) => ({ fieldPath }))
    );

    // If the number of selected fields is equal to the fields in the stream, field selection is disabled because all fields are selected
    if (selectedFields.length === numberOfFieldsInStream) {
      return { primaryKey: compositePrimaryKey, selectedFields: [], fieldSelectionEnabled: false };
    }

    return {
      fieldSelectionEnabled: true,
      selectedFields,
      primaryKey: compositePrimaryKey,
    };
  }

  return {
    primaryKey: compositePrimaryKey,
  };
};

/**
 * Toggles whether a fieldPath is part of the composite primaryKey
 */
export const toggleFieldInPrimaryKey = (
  config: AirbyteStreamConfiguration,
  fieldPath: string[],
  numberOfFieldsInStream: number
): Partial<AirbyteStreamConfiguration> => {
  const fieldIsSelected = !config?.primaryKey?.find((pk) => isEqual(pk, fieldPath));
  let newPrimaryKey: string[][];

  if (!fieldIsSelected) {
    newPrimaryKey = config.primaryKey?.filter((key) => !isEqual(key, fieldPath)) ?? [];
  } else {
    newPrimaryKey = [...(config?.primaryKey ?? []), fieldPath];
  }

  // If field selection is enabled, we need to be sure the new fieldPath is also selected
  if (fieldIsSelected && config?.fieldSelectionEnabled) {
    const previouslySelectedFields = config?.selectedFields || [];
    const selectedFields = mergeFieldPathArrays(previouslySelectedFields, [{ fieldPath }]);

    // If the number of selected fields is equal to the fields in the stream, field selection is disabled because all fields are selected
    if (selectedFields.length === numberOfFieldsInStream) {
      return { primaryKey: newPrimaryKey, selectedFields: [], fieldSelectionEnabled: false };
    }

    return {
      fieldSelectionEnabled: true,
      selectedFields,
      primaryKey: newPrimaryKey,
    };
  }

  return {
    primaryKey: newPrimaryKey,
  };
};
