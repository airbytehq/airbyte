import * as yup from "yup";

import { ConnectionScheduleType } from "core/request/AirbyteClient";

const regexMap = [
  /^(([0-9]|\*)+)/, // seconds
  /^(([0-9]|\*)+)/, // minutes
  /^(([0-9]|\*)+)/, // hours
  /^(([1-9]|\*|\?|L|W)+)/, // day of month
  /^(([1-9]|\*|JAN|FEB|MAR|APR|JUN|JUL|AUG|SEP|OCT|NOV|DEC)+)/, // month
  /^(([1-7]|\*|\?|L|#|SUN|MON|TUE|WED|THU|FRI|SAT|SUN)+)/, // day of week
  /^((\d|\*)+)?/, // year
];

export function validateCronExpression(expression: string): boolean {
  try {
    const cronFields = expression.trim().split(" ");

    if (cronFields.length < 6) {
      throw new Error(`Cron expression "${expression}" is not long enough ${cronFields.length}`);
    }

    cronFields.forEach((field, index) => {
      if (!regexMap[index].test(field)) {
        throw new Error(`${field} did not match regex index ${index}`);
      }
    });
  } catch (e) {
    return false;
  }

  return true;
}

export const scheduleFieldValidationSchema = yup.mixed().when("scheduleType", (scheduleType) => {
  if (scheduleType === ConnectionScheduleType.basic) {
    return yup.object({
      basicSchedule: yup
        .object({
          units: yup.number().required("form.empty.error"),
          timeUnit: yup.string().required("form.empty.error"),
        })
        .defined("form.empty.error"),
    });
  } else if (scheduleType === ConnectionScheduleType.manual) {
    return yup.mixed().notRequired();
  }

  return yup.object({
    cron: yup
      .object({
        cronExpression: yup
          .string()
          .required("form.empty.error")
          .test("validCron", "form.cronExpression.error", (expression) =>
            !expression ? false : validateCronExpression(expression)
          ),
        cronTimeZone: yup.string().required("form.empty.error"),
      })
      .defined("form.empty.error"),
  });
});
