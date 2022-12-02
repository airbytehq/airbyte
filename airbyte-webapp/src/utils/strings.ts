export const convertSnakeToCamel = (value: string) =>
  value.toLowerCase().replace(/([-_][a-z])/g, (group) => group.toUpperCase().replace("-", "").replace("_", ""));
