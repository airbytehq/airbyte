import * as cronValidator from "cron-expression-validator";
import * as yup from "yup";

import { ConnectionScheduleType } from "core/request/AirbyteClient";

export const scheduleFieldValidationSchema = yup.object({
  scheduleData: yup.mixed().when("scheduleType", (scheduleType) => {
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
              !expression ? false : cronValidator.isValidCronExpression(expression)
            ),
          cronTimeZone: yup.string().required("form.empty.error"),
        })
        .defined("form.empty.error"),
    });
  }),
});
