import { SyncSchema } from "./resources/Schema";

export const constructInitialSchemaState = (syncSchema: SyncSchema) => {
  const initialChecked: Array<string> = [];
  syncSchema.streams.map(item =>
    item.fields.forEach(field =>
      field.selected ? initialChecked.push(`${item.name}_${field.name}`) : null
    )
  );

  const formSyncSchema = syncSchema.streams.map((item: any) => ({
    value: item.name,
    label: item.name,
    children: item.fields.map((field: any) => ({
      value: `${item.name}_${field.name}`,
      label: field.name
    }))
  }));

  return {
    formSyncSchema,
    initialChecked
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
