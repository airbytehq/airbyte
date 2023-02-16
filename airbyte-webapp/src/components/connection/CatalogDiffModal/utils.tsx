import { FieldTransform, StreamTransform } from "core/request/AirbyteClient";

import { SortedDiff } from "./types";

export const getSortedDiff = <T extends StreamTransform | FieldTransform>(diffArray?: T[]): SortedDiff<T> => {
  const sortedDiff: SortedDiff<T> = { newItems: [], removedItems: [], changedItems: [] };
  diffArray?.forEach((transform) => {
    if (transform.transformType.includes("add")) {
      sortedDiff.newItems.push(transform);
    }

    if (transform.transformType.includes("remove")) {
      sortedDiff.removedItems.push(transform);
    }

    if (transform.transformType.includes("update")) {
      const { updateFieldSchema } = transform as FieldTransform;
      if (!updateFieldSchema || updateFieldSchema.newSchema.type !== updateFieldSchema.oldSchema.type) {
        // Push any change except except when it's FieldTransform a same -> same type update (e.g. object -> object)
        // because for objects, the properties of that field will be shown as added or removed in the modal
        sortedDiff.changedItems.push(transform);
      }
    }
  });
  return sortedDiff;
};
