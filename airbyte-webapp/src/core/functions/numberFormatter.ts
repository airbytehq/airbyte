export interface INumberNamingFormatter {
  num: number;
  decimalUpto?: number;
}

export const NumberNaming = {
  K: 1000,
  M: 1000000,
  B: 1000000000,
  T: 1000000000000,
  Q: 1000000000000000,
} as const;

export const numberNamingFormatter = ({ num, decimalUpto = 0 }: INumberNamingFormatter): string => {
  if (num >= NumberNaming.K && num < NumberNaming.M) {
    return `${(num / NumberNaming.K).toFixed(decimalUpto)}K`;
  } else if (num >= NumberNaming.M) {
    return `${(num / NumberNaming.M).toFixed(decimalUpto)}M`;
  } else if (num >= NumberNaming.B) {
    return `${(num / NumberNaming.B).toFixed(decimalUpto)}B`;
  } else if (num >= NumberNaming.T) {
    return `${(num / NumberNaming.T).toFixed(decimalUpto)}T`;
  } else if (num >= NumberNaming.Q) {
    return `${(num / NumberNaming.Q).toFixed(decimalUpto)}Q`;
  }
  return `${num}`;
};
