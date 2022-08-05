import { FieldTransform, StreamTransform } from "core/request/AirbyteClient";

export type DiffVerb = "new" | "removed" | "changed";

export interface SortedDiff<T extends StreamTransform | FieldTransform> {
  newItems: T[];
  removedItems: T[];
  changedItems: T[];
}
