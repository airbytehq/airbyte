import { validateCronExpression, validateCronFrequencyOneHourOrMore } from "./validateCronExpression";

// Test cases are taken from http://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html
describe("validateCronExpression", () => {
  it.each`
    expression                                               | isValid
    ${"0 0 12 * * ?"}                                        | ${true}
    ${"0  0  12  *  *  ?  "}                                 | ${true}
    ${"0 0 12 * * ? "}                                       | ${true}
    ${" 0 0 12 * * ?"}                                       | ${true}
    ${"0/5 14,18,3-39,52 * ? JAN,MAR,SEP MON-FRI 2002-2010"} | ${true}
    ${"0 15 10 ? * *"}                                       | ${true}
    ${"0 15 10 * * ?"}                                       | ${true}
    ${"0 15 10 * * ? *"}                                     | ${true}
    ${"0 15 10 * * ? 2005"}                                  | ${true}
    ${"0 * 14 * * ?"}                                        | ${true}
    ${"0 0/5 14 * * ?"}                                      | ${true}
    ${"0 0/5 14,18 * * ?"}                                   | ${true}
    ${"0 0-5 14 * * ?"}                                      | ${true}
    ${"0 10,44 14 ? 3 WED"}                                  | ${true}
    ${"0 15 10 ? * MON-FRI"}                                 | ${true}
    ${"0 15 10 15 * ?"}                                      | ${true}
    ${"0 15 10 L * ?"}                                       | ${true}
    ${"0 15 10 L-2 * ?"}                                     | ${true}
    ${"0 15 10 ? * 6L"}                                      | ${true}
    ${"0 15 10 ? * 6L"}                                      | ${true}
    ${"0 15 10 ? * 6L 2002-2005"}                            | ${true}
    ${"0 15 10 ? * 6#3"}                                     | ${true}
    ${"0 0 12 1/5 * ?"}                                      | ${true}
    ${"0 11 11 11 11 ?"}                                     | ${true}
    ${"* * * * * ?"}                                         | ${true}
    ${"0 0 0 * * ?"}                                         | ${true}
    ${"0 0 1 * * ?"}                                         | ${true}
    ${"0 0 10-19/10 ? * MON-FRI *"}                          | ${true}
    ${"0 0 1 1/1 * ? *"}                                     | ${true}
    ${"0 0 12 * * ?"}                                        | ${true}
    ${"0 0 15 * * ?"}                                        | ${true}
    ${"0 0 17 * * ?"}                                        | ${true}
    ${"0 0 18 * * ?"}                                        | ${true}
    ${"0 0 18 1 * ?"}                                        | ${true}
    ${"0 0 18 2 * ?"}                                        | ${true}
    ${"0 0 2 * * ?"}                                         | ${true}
    ${"0 0 21 * * ?"}                                        | ${true}
    ${"0 0 2 L * ?"}                                         | ${true}
    ${"0 0 3 * * ?"}                                         | ${true}
    ${"0 0 4 * * ?"}                                         | ${true}
    ${"0 0 5 * * ?"}                                         | ${true}
    ${"0 0 6 * * ?"}                                         | ${true}
    ${"0 0 7 * * ?"}                                         | ${true}
    ${"0 0 9 * * ?"}                                         | ${true}
    ${"0 0 9 ? * 5"}                                         | ${true}
    ${"0 1 0 * * ?"}                                         | ${true}
    ${"0 15,45 7-17 ? * MON-FRI"}                            | ${true}
    ${"0 15 6 * * ?"}                                        | ${true}
    ${"0 30 1 * * ?"}                                        | ${true}
    ${"0 30 2 * * ?"}                                        | ${true}
    ${"0 30 6 * * ?"}                                        | ${true}
    ${"0 30 8 ? * MON-FRI *"}                                | ${true}
    ${"0 35 12 ? * 7 "}                                      | ${true}
    ${"0 40 4,16 * * ? *"}                                   | ${true}
    ${"0 45 6 * * ?"}                                        | ${true}
    ${"0 5 0 ? * 7"}                                         | ${true}
    ${"40 4,16 * * * ?"}                                     | ${true}
    ${"wildly invalid"}                                      | ${false}
    ${"* * * * *"}                                           | ${false}
    ${"0 0 0 0 0 0"}                                         | ${false}
  `("'$expression' is valid: $isValid", ({ expression, isValid }) => {
    expect(validateCronExpression(expression)).toEqual(isValid);
  });
});

describe("validateCronFrequencyOverOneHour", () => {
  it.each`
    expression            | isValid
    ${"0 0 12 * * ?"}     | ${true}
    ${"0    0 12 * * ?"}  | ${true}
    ${"0 0 * * * ?"}      | ${true}
    ${"0 * 12 * * ?"}     | ${false}
    ${"* * 12 * * ?"}     | ${false}
    ${"15,45 * 12 * * ?"} | ${false}
    ${"0 15,45 12 * * ?"} | ${false}
    ${"0/10 * * * * ?"}   | ${false}
    ${"0 0/10 * * * ?"}   | ${false}
  `("'$expression' is valid: $isValid", ({ expression, isValid }) => {
    expect(validateCronFrequencyOneHourOrMore(expression)).toEqual(isValid);
  });
});
