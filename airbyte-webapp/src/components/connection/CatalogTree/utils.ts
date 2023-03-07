import { SyncSchemaField } from "core/domain/catalog";

import { IndexerType } from "./PathPopout";

export const flatten = (fArr: SyncSchemaField[], arr: SyncSchemaField[] = []): SyncSchemaField[] =>
  fArr.reduce<SyncSchemaField[]>((acc, f) => {
    acc.push(f);

    if (f.fields?.length) {
      return flatten(f.fields, acc);
    }
    return acc;
  }, arr);

export const getPathType = (required: boolean, shouldDefine: boolean): IndexerType =>
  required ? (shouldDefine ? "required" : "sourceDefined") : null;
