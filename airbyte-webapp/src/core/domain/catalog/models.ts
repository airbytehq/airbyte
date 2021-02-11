export type SyncSchemaField = {
  name: string;
  cleanedName: string;
  type: string;
  key: string;
  // dataType: string;

  fields?: SyncSchemaField[];
};
