import { FieldTransform, StreamTransform } from "core/request/AirbyteClient";

import { SortedDiff } from "./types";

export const getSortedDiff = <T extends StreamTransform | FieldTransform>(diffArray?: T[]): SortedDiff<T> => {
  const sortedDiff: SortedDiff<T> = { newItems: [], removedItems: [], changedItems: [] };
  if (!diffArray) {
    return sortedDiff;
  }

  diffArray.reduce((sortedDiff, transform) => {
    if (transform.transformType.includes("add")) {
      sortedDiff.newItems.push(transform);
    }

    if (transform.transformType.includes("remove")) {
      sortedDiff.removedItems.push(transform);
    }

    if (transform.transformType.includes("update")) {
      sortedDiff.changedItems.push(transform);
    }

    return sortedDiff;
  }, sortedDiff);
  return sortedDiff;
};
