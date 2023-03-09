import { renderHook } from "@testing-library/react-hooks";
import React from "react";
import { IntlProvider } from "react-intl";

import { AirbyteConnectorData, useTranslateDataType } from "./useTranslateDataType";
import messages from "../locales/en.json";

const wrapper: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => (
  <IntlProvider messages={messages} locale="en">
    {children}
  </IntlProvider>
);
const translate = (translatable: AirbyteConnectorData) => {
  const {
    result: { current },
  } = renderHook(() => useTranslateDataType(translatable), { wrapper });
  return current;
};

describe("useTranslateDataType", () => {
  it.each([
    "string",
    "date",
    "timestamp_with_timezone",
    "timestamp_without_timezone",
    "datetime",
    "integer",
    "big_integer",
    "number",
    "big_number",
    "array",
    "object",
    "untyped",
    "union",
    "boolean",
  ])("should translate %", (type) => {
    const current = translate({ type });
    expect(current).toMatchSnapshot();
    expect(current).not.toBe(type);
  });

  describe("union type", () => {
    it("should use union type if oneOf is set", () => {
      expect(translate({ type: "string", oneOf: [] })).toBe("Union");
    });
    it("should use union type if anyOf is set", () => {
      expect(translate({ type: "string", anyOf: [] })).toBe("Union");
    });
    it("should use union type if anyOf and oneOf is set", () => {
      expect(translate({ type: "string", anyOf: [], oneOf: [] })).toBe("Union");
    });
  });

  it("should be unknown if the type is not recognized", () => {
    expect(translate({ type: "potato" })).toBe("Unknown");
  });

  it("should return untyped when given no values", () => {
    // @ts-expect-error Using this method internally should demand a type
    expect(translate({})).toBe("Unknown");
  });

  describe("translation priority", () => {
    it("should use airbyte_type over format or type", () => {
      expect(translate({ type: "string", format: "date", airbyte_type: "big_number" })).toBe("Big Number");
    });
    it("should use format over type", () => {
      expect(translate({ type: "string", format: "date" })).toBe("Date");
    });
    it("should use oneOf/anyOf over everything else", () => {
      expect(translate({ type: "string", format: "date", airbyte_type: "big_number", oneOf: [] })).toBe("Union");
    });
  });
});
