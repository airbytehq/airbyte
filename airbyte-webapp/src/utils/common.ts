export function isDefined<T>(a: T | null | undefined): a is Exclude<T, null | undefined> {
  return a !== undefined && a !== null;
}

export const getKeyProp = (uniqueIdentifier?: number | string): string => {
  if (uniqueIdentifier) {
    return `${uniqueIdentifier}_${Math.random() * 10000000000000000000 * Math.random()}`;
  }
  return `${Math.random() * 10000000000000000000 * Math.random()}`;
};

export const remainingDaysForFreeTrial = (expiresTime: number): number => {
  const currentDate: Date = new Date();
  const expiryDate: Date = new Date(expiresTime * 1000);
  const diff = expiryDate.getTime() - currentDate.getTime();
  const diffDays = Math.ceil(diff / (1000 * 60 * 60 * 24));
  return diffDays;
};
