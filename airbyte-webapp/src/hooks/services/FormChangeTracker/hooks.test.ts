import { act, renderHook } from "@testing-library/react-hooks";

import { useUniqueFormId, useFormChangeTrackerService, useChangedFormsById } from "./hooks";

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

describe("#useFormChangeTrackerService", () => {
  afterEach(() => {
    const { result } = renderHook(() => useChangedFormsById());
    act(() => {
      const [, setChangedFormsById] = result.current;
      setChangedFormsById({});
    });
  });

  it("hasFormChanges returns true when there are form changes", () => {
    const { result } = renderHook(() => useFormChangeTrackerService());

    act(() => {
      result.current.trackFormChange("a", false);
      result.current.trackFormChange("b", true);
      result.current.trackFormChange("c", false);
    });

    expect(result.current.hasFormChanges).toBe(true);
  });

  it("hasFormChanges returns false when there are no form changes", () => {
    const { result } = renderHook(() => useFormChangeTrackerService());

    act(() => {
      result.current.trackFormChange("a", false);
      result.current.trackFormChange("c", false);
    });

    expect(result.current.hasFormChanges).toBe(false);
  });
});
