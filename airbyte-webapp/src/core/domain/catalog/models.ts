export interface SyncSchemaField {
  cleanedName: string;
  type: string;
  key: string;
  path: string[];
  airbyte_type?: string;
  format?: string;
  fields?: SyncSchemaField[];
}

export class SyncSchemaFieldObject {
  static isPrimitive(field: SyncSchemaField): boolean {
    return !(field.type === "object" || field.type === "array");
  }
}
