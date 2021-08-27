import { applyProviders } from "./configProviders";
import { DeepPartial, Provider } from "./types";

type Value = {
  prop1: {
    innerProp: string;
    innerProp2: string;
  };
  prop2: {
    innerProp: string;
    innerProp2: string;
  };
  prop3: {
    innerProp: string;
  };
};
describe("applyProviders", function () {
  test("should deepMerge config returned from providers", async () => {
    const defaultValue: Value = {
      prop1: {
        innerProp: "Alex",
        innerProp2: "Phil",
      },
      prop2: {
        innerProp: "Alex",
        innerProp2: "Phil",
      },
      prop3: {
        innerProp: "1",
      },
    };
    const providers: [Provider<Value>, ...Provider<DeepPartial<Value>>[]] = [
      async () => defaultValue,
      async () => ({
        prop1: {
          innerProp: "John",
        },
        prop2: {
          innerProp: "Tom",
        },
      }),
    ];

    const result = await applyProviders(providers);
    expect(result).toEqual({
      prop1: {
        innerProp: "John",
        innerProp2: "Phil",
      },
      prop2: {
        innerProp: "Tom",
        innerProp2: "Phil",
      },
      prop3: {
        innerProp: "1",
      },
    });
  });
});
