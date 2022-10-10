import { ConnectionScheduleType } from "core/request/AirbyteClient";

import { scheduleFieldValidationSchema } from "./validationSchema";

// Test cases are taken from http://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html
describe("validateCronExpression", () => {
  it.each`
    expression                    | isValid
    ${"0 0 12 * * ?"}             | ${true}
    ${"0 15 10 ? * *"}            | ${true}
    ${"0 15 10 * * ?"}            | ${true}
    ${"0 15 10 * * ? *"}          | ${true}
    ${"0 15 10 * * ? 2005"}       | ${true}
    ${"0 * 14 * * ?"}             | ${true}
    ${"0 0/5 14 * * ?"}           | ${true}
    ${"0 0/5 14,18 * * ?"}        | ${true}
    ${"0 0-5 14 * * ?"}           | ${true}
    ${"0 10,44 14 ? 3 WED"}       | ${true}
    ${"0 15 10 ? * MON-FRI"}      | ${true}
    ${"0 15 10 15 * ?"}           | ${true}
    ${"0 15 10 L * ?"}            | ${true}
    ${"0 15 10 L-2 * ?"}          | ${true}
    ${"0 15 10 ? * 6L"}           | ${true}
    ${"0 15 10 ? * 6L"}           | ${true}
    ${"0 15 10 ? * 6L 2002-2005"} | ${true}
    ${"0 15 10 ? * 6#3"}          | ${true}
    ${"0 0 12 1/5 * ?"}           | ${true}
    ${"0 11 11 11 11 ?"}          | ${true}
    ${"wildly invalid"}           | ${false}
    ${"* * * * *"}                | ${false}
  `("'$expression' is valid: $isValid", async ({ expression, isValid }) => {
    expect(
      await scheduleFieldValidationSchema.isValid({
        scheduleType: ConnectionScheduleType.cron,
        scheduleData: { cron: { cronExpression: expression, cronTimeZone: "Some time zone" } },
      })
    ).toEqual(isValid);
  });
});
