import { convertSnakeToCamel } from "./strings";

describe("convertSnakeToCamel", () => {
  it("correctly convert snake case to camel case", () => {
    expect(convertSnakeToCamel("TO_CAMEL")).toEqual("toCamel");
    expect(convertSnakeToCamel("to_camel")).toEqual("toCamel");
    expect(convertSnakeToCamel("test_long_snake_case")).toEqual("testLongSnakeCase");
  });
});
