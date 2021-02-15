export type SyncSchemaField = {
  name: string;
  cleanedName: string;
  type: string;
  key: string;

  fields?: SyncSchemaField[];
};
