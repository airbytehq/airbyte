export function isDefined<T>(a: T | null | undefined): a is Exclude<T, null | undefined> {
  return a !== undefined && a !== null;
}

export const getKeyProp = (uniqueIdentifier?: number | string): string => {
  if (uniqueIdentifier) {
    return `${uniqueIdentifier}_${Math.random() * 10000000000000000000 * Math.random()}`;
  }
  return `${Math.random() * 10000000000000000000 * Math.random()}`;
};
