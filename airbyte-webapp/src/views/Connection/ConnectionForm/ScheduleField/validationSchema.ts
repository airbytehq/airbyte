import * as yup from "yup";

import { ConnectionScheduleType } from "core/request/AirbyteClient";

const regexMap = [
  /^((\d|\*)+)/, // seconds
  /^((\d|\*)+)/, // minutes
  /^((\d|\*)+)/, // hours
  /^((\d|\*|\?|L|W)+)/, // day of month
  /^((\d|\*|JAN|FEB|MAR|APR|JUN|JUL|AUG|SEP|OCT|NOV|DEC)+)/, // month
  /^((\d|\*|\?|L|#|SUN|MON|TUE|WED|THU|FRI|SAT|SUN)+)/, // day of week
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
