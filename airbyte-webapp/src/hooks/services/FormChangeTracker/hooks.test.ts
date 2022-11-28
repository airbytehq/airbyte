import { renderHook } from "@testing-library/react-hooks";

import { useUniqueFormId } from "./hooks";

describe("#useUniqueFormId", () => {
  it("should use what is passed into it", () => {
    const {
      result: { current },
    } = renderHook(() => useUniqueFormId("asdf"));
    expect(current).toBe("asdf");
  });

  it("should generate an id like /form_/", () => {
    const {
      result: { current },
    } = renderHook(useUniqueFormId);
    expect(current).toMatch(/form_/);
  });
});
