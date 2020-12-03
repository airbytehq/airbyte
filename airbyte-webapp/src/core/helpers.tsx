import { SyncSchema } from "./resources/Schema";

export const constructInitialSchemaState = (syncSchema: SyncSchema) => {
  const initialChecked: Array<string> = [];
  syncSchema.streams.map(item =>
    item.fields.forEach(field =>
      field.selected ? initialChecked.push(`${item.name}_${field.name}`) : null
    )
  );

  const allSchemaChecked: Array<string> = [];
  syncSchema.streams.map(item =>
    item.fields.forEach(field =>
      allSchemaChecked.push(`${item.name}_${field.name}`)
    )
  );

  const syncModeInitialState: Array<any> = [];
  syncSchema.streams.map(item => ({
    value: item.name,
    syncMode: item.syncMode
  }));

  const formSyncSchema = syncSchema.streams.map((item: any) => ({
    value: item.name,
    label: item.name,
    supportedSyncModes: item.supportedSyncModes,
    syncMode: item.syncMode || "full_refresh",
    cleanedName: item.cleanedName,
    children: item.fields.map((field: any) => ({
      value: `${item.name}_${field.name}`,
      label: field.name,
      dataType: field.dataType,
      cleanedName: item.cleanedName
    }))
  }));

  return {
    formSyncSchema,
    initialChecked,
    allSchemaChecked,
    syncModeInitialState
  };
};

export const constructNewSchema = (
  syncSchema: SyncSchema,
  checkedState: string[]
) => {
  const newSyncSchema = {
    streams: syncSchema.streams.map(item => ({
      ...item,
      fields: item.fields.map(field => ({
        ...field,
        selected: checkedState.includes(`${item.name}_${field.name}`)
      }))
    }))
  };

  return newSyncSchema;
};
