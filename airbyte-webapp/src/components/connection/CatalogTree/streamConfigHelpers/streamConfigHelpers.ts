import isEqual from "lodash/isEqual";

import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";

/**
 * Updates the cursor field in AirbyteStreamConfiguration
 */
export const updateCursorField = (
  config: AirbyteStreamConfiguration,
  selectedCursorField: string[],
  numberOfFieldsInStream: number
): Partial<AirbyteStreamConfiguration> => {
  const previouslySelectedFields = config?.selectedFields || [];

  // If field selection is enabled, we need to be sure the new cursor is also selected
  if (config?.fieldSelectionEnabled && !previouslySelectedFields.find((field) => isEqual(field, selectedCursorField))) {
    if (previouslySelectedFields.length === numberOfFieldsInStream - 1) {
      return { cursorField: selectedCursorField, selectedFields: [], fieldSelectionEnabled: false };
    }
    return {
      fieldSelectionEnabled: true,
      selectedFields: [...previouslySelectedFields, { fieldPath: selectedCursorField }],
      cursorField: selectedCursorField,
    };
  }
  return { cursorField: selectedCursorField };
};

/**
 * Overwrites the entire primaryKey value in AirbyteStreamConfiguration.
 */
export const updatePrimaryKey = (
  config: AirbyteStreamConfiguration,
  compositePrimaryKey: string[][],
  numberOfFieldsInStream: number
): Partial<AirbyteStreamConfiguration> => {
  const previouslySelectedFields = config?.selectedFields || [];

  // If field selection is enabled, we need to be sure each fieldPath in the new primary key is also selected
  if (
    config?.fieldSelectionEnabled &&
    !compositePrimaryKey.some((fieldPath) => previouslySelectedFields.find((field) => isEqual(field, fieldPath)))
  ) {
    // If the fieldPath being added to the primaryKey is the only unselected field,
    // we can actually just disable field selection, since all fields are now selected.
    if (previouslySelectedFields.length === numberOfFieldsInStream - 1) {
      return { primaryKey: compositePrimaryKey, selectedFields: [], fieldSelectionEnabled: false };
    }
    return {
      fieldSelectionEnabled: true,
      selectedFields: [...previouslySelectedFields, ...compositePrimaryKey.map((fieldPath) => ({ fieldPath }))],
      primaryKey: compositePrimaryKey,
    };
  }

  return {
    primaryKey: compositePrimaryKey,
  };
};

/**
 * Adds a single fieldPath to the composite primaryKey
 */
export const addFieldToPrimaryKey = (
  config: AirbyteStreamConfiguration,
  fieldPath: string[],
  numberOfFieldsInStream: number
): Partial<AirbyteStreamConfiguration> => {
  const fieldIsSelected = !config?.primaryKey?.find((pk) => isEqual(pk, fieldPath));
  const previouslySelectedFields = config?.selectedFields || [];
  let newPrimaryKey: string[][];

  if (!fieldIsSelected) {
    newPrimaryKey = config.primaryKey?.filter((key) => !isEqual(key, fieldPath)) ?? [];
  } else {
    newPrimaryKey = [...(config?.primaryKey ?? []), fieldPath];
  }

  // If field selection is enabled, we need to be sure the new fieldPath is also selected
  if (
    fieldIsSelected &&
    config?.fieldSelectionEnabled &&
    !previouslySelectedFields.find((field) => isEqual(field, fieldPath))
  ) {
    if (previouslySelectedFields.length === numberOfFieldsInStream - 1) {
      return { primaryKey: newPrimaryKey, selectedFields: [], fieldSelectionEnabled: false };
    }
    return {
      fieldSelectionEnabled: true,
      selectedFields: [...previouslySelectedFields, { fieldPath }],
      primaryKey: newPrimaryKey,
    };
  }

  return {
    primaryKey: newPrimaryKey,
  };
};
