import { renderHook } from "@testing-library/react-hooks";

import FrequencyConfig from "config/FrequencyConfig.json";
import { ConnectionScheduleTimeUnit } from "core/request/AirbyteClient";
import { TestWrapper as wrapper } from "utils/testutils";

import { useFrequencyDropdownData } from "./formConfig";

describe("useFrequencyDropdownData", () => {
  it("should return only default frequencies when no additional frequency is provided", () => {
    const { result } = renderHook(() => useFrequencyDropdownData(undefined), { wrapper });
    expect(result.current.map((item) => item.value)).toEqual(FrequencyConfig.map((item) => item.config));
  });

  it("should return only default frequencies when additional frequency is already present", () => {
    const additionalFrequency = {
      units: 1,
      timeUnit: ConnectionScheduleTimeUnit["hours"],
    };
    const { result } = renderHook(() => useFrequencyDropdownData(additionalFrequency), { wrapper });
    expect(result.current.map((item) => item.value)).toEqual(FrequencyConfig.map((item) => item.config));
  });

  it("should include additional frequency when provided and unique", () => {
    const additionalFrequency = {
      units: 7,
      timeUnit: ConnectionScheduleTimeUnit["minutes"],
    };
    const { result } = renderHook(() => useFrequencyDropdownData(additionalFrequency), { wrapper });

    expect(result.current.length).toEqual(FrequencyConfig.length + 1);
    expect(result.current).toContainEqual({ label: "Every 7 minutes", value: { units: 7, timeUnit: "minutes" } });
  });
});
