export function formatJson(json: unknown, order?: boolean): string {
  return JSON.stringify(order ? orderKeys(json) : json, null, 2);
}

function orderKeys(obj: unknown): unknown {
  if (Array.isArray(obj)) {
    return obj.map(orderKeys);
  }
  if (typeof obj !== "object" || obj === null) {
    return obj;
  }
  return Object.fromEntries(
    Object.entries(obj)
      .sort(([key1], [key2]) => {
        if (key1 < key2) {
          return -1;
        }
        if (key1 > key2) {
          return 1;
        }

        // names must be equal
        return 0;
      })
      .map(([key, val]) => [key, orderKeys(val)])
  );
}
