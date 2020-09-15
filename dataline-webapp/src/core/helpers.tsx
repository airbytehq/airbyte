import { SyncSchema } from "./resources/Schema";

export const constructInitialSchemaState = (syncSchema: SyncSchema) => {
  const initialChecked: Array<string> = [];
  syncSchema.tables.map(item =>
    item.columns.forEach(column =>
      column.selected
        ? initialChecked.push(`${item.name}_${column.name}`)
        : null
    )
  );

  const formSyncSchema = syncSchema.tables.map((item: any) => ({
    value: item.name,
    label: item.name,
    children: item.columns.map((column: any) => ({
      value: `${item.name}_${column.name}`,
      label: column.name
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
    tables: syncSchema.tables.map(item => ({
      ...item,
      columns: item.columns.map(column => ({
        ...column,
        selected: checkedState.includes(`${item.name}_${column.name}`)
      }))
    }))
  };

  return newSyncSchema;
};
