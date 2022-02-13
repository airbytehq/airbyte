import { SyncSchemaField } from "core/domain/catalog";

export const flatten = (
  fArr: SyncSchemaField[],
  arr: SyncSchemaField[] = []
): SyncSchemaField[] =>
  fArr.reduce<SyncSchemaField[]>((acc, f) => {
    acc.push(f);

    if (f.fields?.length) {
      return flatten(f.fields, acc);
    }
    return acc;
  }, arr);
