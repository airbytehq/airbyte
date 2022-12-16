import { act } from "@testing-library/react";
import { renderHook } from "@testing-library/react-hooks";
import React from "react";
import { EMPTY, Subject } from "rxjs";

import { Experiments } from "./experiments";
import { ExperimentProvider, ExperimentService, useExperiment } from "./ExperimentService";

type TestExperimentValueType = Experiments["connector.orderOverwrite"];

const TEST_EXPERIMENT_KEY = "connector.orderOverwrite";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const getExperiment: ExperimentService["getExperiment"] = (key): any => {
  if (key === TEST_EXPERIMENT_KEY) {
    return { test: 13 };
  }
  throw new Error(`${key} not mocked for testing`);
};

describe("ExperimentService", () => {
  describe("useExperiment", () => {
    it("should return the value from the ExperimentService if provided", () => {
      const wrapper: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => (
        <ExperimentProvider
          value={{
            getExperiment,
            getExperimentChanges$: () => EMPTY,
          }}
        >
          {children}
        </ExperimentProvider>
      );
      const { result } = renderHook(() => useExperiment(TEST_EXPERIMENT_KEY, { test: 10 }), { wrapper });
      expect(result.current).toEqual({ test: 13 });
    });

    it("should return the defaultValue if ExperimentService provides undefined", () => {
      const wrapper: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => (
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        <ExperimentProvider value={{ getExperiment: () => undefined as any, getExperimentChanges$: () => EMPTY }}>
          {children}
        </ExperimentProvider>
      );
      const { result } = renderHook(() => useExperiment(TEST_EXPERIMENT_KEY, { test: 10 }), { wrapper });
      expect(result.current).toEqual({ test: 10 });
    });

    it("should return the default value if no ExperimentService is provided", () => {
      const { result } = renderHook(() => useExperiment(TEST_EXPERIMENT_KEY, { test: 42 }));
      expect(result.current).toEqual({ test: 42 });
    });

    it("should rerender whenever the ExperimentService emits a new value", () => {
      const subject = new Subject<TestExperimentValueType>();
      const wrapper: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => (
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        <ExperimentProvider value={{ getExperiment, getExperimentChanges$: () => subject.asObservable() as any }}>
          {children}
        </ExperimentProvider>
      );
      const { result } = renderHook(() => useExperiment(TEST_EXPERIMENT_KEY, { test: 10 }), {
        wrapper,
      });
      expect(result.current).toEqual({ test: 13 });
      act(() => {
        subject.next({ test: 9000 });
      });
      expect(result.current).toEqual({ test: 9000 });
    });
  });
});
