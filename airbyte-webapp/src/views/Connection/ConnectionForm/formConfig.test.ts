import { renderHook } from "@testing-library/react-hooks";
import mockDestinationDefinition from "test-utils/mock-data//mockDestinationDefinition.json";
import mockConnection from "test-utils/mock-data/mockConnection.json";
import { TestWrapper as wrapper } from "test-utils/testutils";

import { frequencyConfig } from "config/frequencyConfig";
import { NormalizationType } from "core/domain/connection";
import {
  ConnectionScheduleTimeUnit,
  DestinationDefinitionSpecificationRead,
  OperationRead,
  WebBackendConnectionRead,
} from "core/request/AirbyteClient";

import { mapFormPropsToOperation, useFrequencyDropdownData, useInitialValues } from "./formConfig";

describe("#useFrequencyDropdownData", () => {
  it("should return only default frequencies when no additional frequency is provided", () => {
    const { result } = renderHook(() => useFrequencyDropdownData(undefined), { wrapper });
    expect(result.current.map((item) => item.value)).toEqual(frequencyConfig);
  });

  it("should return only default frequencies when additional frequency is already present", () => {
    const additionalFrequency = {
      basicSchedule: {
        units: 1,
        timeUnit: ConnectionScheduleTimeUnit["hours"],
      },
    };
    const { result } = renderHook(() => useFrequencyDropdownData(additionalFrequency), { wrapper });
    expect(result.current.map((item) => item.value)).toEqual(frequencyConfig);
  });

  it("should include additional frequency when provided and unique", () => {
    const additionalFrequency = {
      basicSchedule: {
        units: 7,
        timeUnit: ConnectionScheduleTimeUnit["minutes"],
      },
    };
    const { result } = renderHook(() => useFrequencyDropdownData(additionalFrequency), { wrapper });

    expect(result.current.length).toEqual(frequencyConfig.length + 1);
    expect(result.current).toContainEqual({ label: "Every 7 minutes", value: { units: 7, timeUnit: "minutes" } });
  });
});

describe("#mapFormPropsToOperation", () => {
  const workspaceId = "asdf";
  const normalization: OperationRead = {
    workspaceId,
    operationId: "asdf",
    name: "asdf",
    operatorConfiguration: {
      operatorType: "normalization",
    },
  };

  it("should add any included transformations", () => {
    expect(
      mapFormPropsToOperation(
        {
          transformations: [normalization],
        },
        undefined,
        "asdf"
      )
    ).toEqual([normalization]);
  });

  it("should add a basic normalization if normalization is set to basic", () => {
    expect(
      mapFormPropsToOperation(
        {
          normalization: NormalizationType.basic,
        },

        undefined,
        workspaceId
      )
    ).toEqual([
      {
        name: "Normalization",
        operatorConfiguration: {
          normalization: {
            option: "basic",
          },
          operatorType: "normalization",
        },
        workspaceId,
      },
    ]);
  });

  it("should include any provided initial operations and not include the basic normalization operation when normalization type is basic", () => {
    expect(
      mapFormPropsToOperation(
        {
          normalization: NormalizationType.basic,
        },
        [normalization],
        workspaceId
      )
    ).toEqual([normalization]);
  });

  it("should not include any provided initial operations and not include the basic normalization operation when normalization type is raw", () => {
    expect(
      mapFormPropsToOperation(
        {
          normalization: NormalizationType.raw,
        },
        [normalization],
        workspaceId
      )
    ).toEqual([]);
  });

  it("should include provided transformations when normalization type is raw, but not any provided normalizations", () => {
    expect(
      mapFormPropsToOperation(
        {
          normalization: NormalizationType.raw,
          transformations: [normalization],
        },
        [normalization],
        workspaceId
      )
    ).toEqual([normalization]);
  });

  it("should include provided transformations and normalizations when normalization type is basic", () => {
    expect(
      mapFormPropsToOperation(
        {
          normalization: NormalizationType.basic,
          transformations: [normalization],
        },
        [normalization],
        workspaceId
      )
    ).toEqual([normalization, normalization]);
  });

  it("should include provided transformations and default normalization when normalization type is basic and no normalizations have been provided", () => {
    expect(
      mapFormPropsToOperation(
        {
          normalization: NormalizationType.basic,
          transformations: [normalization],
        },
        undefined,
        workspaceId
      )
    ).toEqual([
      {
        name: "Normalization",
        operatorConfiguration: {
          normalization: {
            option: "basic",
          },
          operatorType: "normalization",
        },
        workspaceId,
      },
      normalization,
    ]);
  });
});

describe("#useInitialValues", () => {
  it("should generate initial values w/ no edit mode", () => {
    const { result } = renderHook(() =>
      useInitialValues(
        mockConnection as WebBackendConnectionRead,
        mockDestinationDefinition as DestinationDefinitionSpecificationRead
      )
    );
    expect(result).toMatchSnapshot();
  });

  it("should generate initial values w/ edit mode: false", () => {
    const { result } = renderHook(() =>
      useInitialValues(
        mockConnection as WebBackendConnectionRead,
        mockDestinationDefinition as DestinationDefinitionSpecificationRead,
        false
      )
    );
    expect(result).toMatchSnapshot();
  });

  it("should generate initial values w/ edit mode: true", () => {
    const { result } = renderHook(() =>
      useInitialValues(
        mockConnection as WebBackendConnectionRead,
        mockDestinationDefinition as DestinationDefinitionSpecificationRead,
        true
      )
    );
    expect(result).toMatchSnapshot();
  });

  // This is a low-priority test
  it.todo(
    "should test for supportsDbt+initialValues.transformations and supportsNormalization+initialValues.normalization"
  );
});
