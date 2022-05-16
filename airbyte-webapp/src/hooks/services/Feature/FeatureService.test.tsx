import { act, renderHook } from "@testing-library/react-hooks";
import React from "react";

import { ConfigContext, configContext } from "config";
import { TestWrapper } from "utils/testutils";

import { FeatureService, useFeatureRegisterValues, useFeatureService } from "./FeatureService";
import { FeatureItem } from "./types";

const predefinedFeatures = [
  {
    id: FeatureItem.AllowCustomDBT,
  },
];

const wrapper: React.FC = ({ children }) => (
  <TestWrapper>
    <configContext.Provider
      value={
        {
          config: { features: predefinedFeatures },
        } as unknown as ConfigContext
      }
    >
      <FeatureService>{children}</FeatureService>
    </configContext.Provider>
  </TestWrapper>
);

describe("FeatureService", () => {
  test("should register and unregister features", async () => {
    const { result } = renderHook(() => useFeatureService(), {
      wrapper,
    });

    expect(result.current.features).toEqual(predefinedFeatures);

    act(() => {
      result.current.registerFeature([
        {
          id: FeatureItem.AllowCreateConnection,
        },
      ]);
    });

    expect(result.current.features).toEqual([
      ...predefinedFeatures,
      {
        id: FeatureItem.AllowCreateConnection,
      },
    ]);

    act(() => {
      result.current.unregisterFeature([FeatureItem.AllowCreateConnection]);
    });

    expect(result.current.features).toEqual(predefinedFeatures);
  });
});

describe("useFeatureRegisterValues", () => {
  test("should register more than 1 feature", async () => {
    const { result } = renderHook(
      () => {
        useFeatureRegisterValues([{ id: FeatureItem.AllowCreateConnection }]);
        useFeatureRegisterValues([{ id: FeatureItem.AllowSync }]);

        return useFeatureService();
      },
      {
        initialProps: { initialValue: 0 },
        wrapper,
      }
    );

    expect(result.current.features).toEqual([
      ...predefinedFeatures,
      { id: FeatureItem.AllowCreateConnection },
      { id: FeatureItem.AllowSync },
    ]);

    act(() => {
      result.current.unregisterFeature([FeatureItem.AllowCreateConnection]);
    });

    expect(result.current.features).toEqual([...predefinedFeatures, { id: FeatureItem.AllowSync }]);
  });
});
