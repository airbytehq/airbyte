export type SyncSchemaField = {
  name: string;
  cleanedName: string;
  type: string;
  key: string;

  fields?: SyncSchemaField[];
};

export class SyncSchemaFieldObject {
  static isPrimitive(field: SyncSchemaField): boolean {
    return !(field.type === "object" || field.type === "array");
  }
}
