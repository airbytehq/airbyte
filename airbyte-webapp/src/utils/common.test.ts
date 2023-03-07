import { isDefined } from "./common";

it.each([
  [null, false],
  [undefined, false],
  ["", true],
  ["0", true],
  [0, true],
  [[], true],
  [{}, true],
])("should pass .isDefined(%i)", (a, expected) => {
  expect(isDefined(a)).toEqual(expected);
});
