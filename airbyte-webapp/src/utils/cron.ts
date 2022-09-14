// This comes from the fact that parseInt trims characters coming
// after digits and consider it a valid int, so `1*` becomes `1`.
const safeParseInt = (value: string): number => {
  if (/^\d+$/.test(value)) {
    return Number(value);
  }
  return NaN;
};

const isWildcard = (value: string): boolean => {
  return value === "*";
};

const isQuestionMark = (value: string): boolean => {
  return value === "?";
};

const isInRange = (value: number, start: number, stop: number): boolean => {
  return value >= start && value <= stop;
};

const isValidRange = (value: string, start: number, stop: number): boolean => {
  const sides = value.split("-");
  switch (sides.length) {
    case 1:
      return isWildcard(value) || isInRange(safeParseInt(value), start, stop);
    case 2:
      const [small, big] = sides.map((side: string): number => safeParseInt(side));
      return small <= big && isInRange(small, start, stop) && isInRange(big, start, stop);
    default:
      return false;
  }
};

const isValidStep = (value: string | undefined): boolean => {
  return value === undefined || (value.search(/[^\d]/) === -1 && safeParseInt(value) > 0);
};

const validateForRange = (value: string, start: number, stop: number): boolean => {
  if (value.search(/[^\d-,/*]/) !== -1) {
    return false;
  }

  const list = value.split(",");
  return list.every((condition: string): boolean => {
    const splits = condition.split("/");
    // Prevents `*/ * * * *` from being accepted.
    if (condition.trim().endsWith("/")) {
      return false;
    }

    // Prevents `*/*/* * * * *` from being accepted
    if (splits.length > 2) {
      return false;
    }

    // If we don't have a `/`, right will be undefined which is considered a valid step if we don't a `/`.
    const [left, right] = splits;
    return isValidRange(left, start, stop) && isValidStep(right);
  });
};

const hasValidSeconds = (seconds: string): boolean => {
  return isQuestionMark(seconds) || validateForRange(seconds, 0, 59);
};

const hasValidMinutes = (minutes: string): boolean => {
  return validateForRange(minutes, 0, 59);
};

const hasValidHours = (hours: string): boolean => {
  return validateForRange(hours, 0, 23);
};

const hasValidDays = (days: string, allowBlankDay?: boolean): boolean => {
  return (allowBlankDay && isQuestionMark(days)) || validateForRange(days, 1, 31);
};

const monthAlias: Record<string, string> = {
  jan: "1",
  feb: "2",
  mar: "3",
  apr: "4",
  may: "5",
  jun: "6",
  jul: "7",
  aug: "8",
  sep: "9",
  oct: "10",
  nov: "11",
  dec: "12",
};

const hasValidMonths = (months: string, alias?: boolean): boolean => {
  // Prevents alias to be used as steps
  if (months.search(/\/[a-zA-Z]/) !== -1) {
    return false;
  }

  if (alias) {
    const remappedMonths = months.toLowerCase().replace(/[a-z]{3}/g, (match: string): string => {
      return monthAlias[match] === undefined ? match : monthAlias[match];
    });
    // If any invalid alias was used, it won't pass the other checks as there will be non-numeric values in the months
    return validateForRange(remappedMonths, 1, 12);
  }

  return validateForRange(months, 1, 12);
};

const weekdaysAlias: Record<string, string> = {
  sun: "0",
  mon: "1",
  tue: "2",
  wed: "3",
  thu: "4",
  fri: "5",
  sat: "6",
};

const hasValidWeekdays = (
  weekdays: string,
  alias?: boolean,
  allowBlankDay?: boolean,
  allowSevenAsSunday?: boolean
): boolean => {
  // If there is a question mark, checks if the allowBlankDay flag is set
  if (allowBlankDay && isQuestionMark(weekdays)) {
    return true;
  } else if (!allowBlankDay && isQuestionMark(weekdays)) {
    return false;
  }

  // Prevents alias to be used as steps
  if (weekdays.search(/\/[a-zA-Z]/) !== -1) {
    return false;
  }

  if (alias) {
    const remappedWeekdays = weekdays.toLowerCase().replace(/[a-z]{3}/g, (match: string): string => {
      return weekdaysAlias[match] === undefined ? match : weekdaysAlias[match];
    });
    // If any invalid alias was used, it won't pass the other checks as there will be non-numeric values in the weekdays
    return validateForRange(remappedWeekdays, 0, allowSevenAsSunday ? 7 : 6);
  }

  return validateForRange(weekdays, 0, allowSevenAsSunday ? 7 : 6);
};

const hasCompatibleDayFormat = (days: string, weekdays: string, allowBlankDay?: boolean) => {
  return !(allowBlankDay && isQuestionMark(days) && isQuestionMark(weekdays));
};

const split = (cron: string): string[] => {
  return cron.trim().split(/\s+/);
};

interface Options {
  alias: boolean;
  seconds: boolean;
  allowBlankDay: boolean;
  allowSevenAsSunday: boolean;
}

const defaultOptions: Options = {
  alias: false,
  seconds: false,
  allowBlankDay: false,
  allowSevenAsSunday: false,
};

export const isValidCron = (cron: string, options?: Partial<Options>): boolean => {
  options = { ...defaultOptions, ...options };

  const splits = split(cron);

  if (splits.length > (options.seconds ? 6 : 5) || splits.length < 5) {
    return false;
  }

  const checks: boolean[] = [];
  if (splits.length === 6) {
    const seconds = splits.shift();
    if (seconds) {
      checks.push(hasValidSeconds(seconds));
    }
  }

  // We could only check the steps gradually and return false on the first invalid block,
  // However, this won't have any performance impact so why bother for now.
  const [minutes, hours, days, months, weekdays] = splits;
  checks.push(hasValidMinutes(minutes));
  checks.push(hasValidHours(hours));
  checks.push(hasValidDays(days, options.allowBlankDay));
  checks.push(hasValidMonths(months, options.alias));
  checks.push(hasValidWeekdays(weekdays, options.alias, options.allowBlankDay, options.allowSevenAsSunday));
  checks.push(hasCompatibleDayFormat(days, weekdays, options.allowBlankDay));

  return checks.every(Boolean);
};
