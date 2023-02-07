export interface SyncSchemaField {
  cleanedName: string;
  type: string;
  key: string;
  path: string[];
  $ref?: string;
  airbyte_type?: string;
  format?: string;
  fields?: SyncSchemaField[];
}

export class SyncSchemaFieldObject {
  static isPrimitive(field: SyncSchemaField): boolean {
    return !(field.type === "object" || field.type === "array");
  }

  static isNestedField(field: SyncSchemaField): boolean {
    return field.path.length > 1;
  }
}
