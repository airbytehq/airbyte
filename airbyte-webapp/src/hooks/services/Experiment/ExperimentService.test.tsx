import { act } from "@testing-library/react";
import { renderHook } from "@testing-library/react-hooks";
import React from "react";
import { EMPTY, Subject } from "rxjs";

import { Experiments } from "./experiments";
import { ExperimentProvider, useExperiment } from "./ExperimentService";

describe("ExperimentService", () => {
  describe("useExperiment", () => {
    it("should return the value from the ExperimentService if provided", () => {
      const wrapper: React.FC = ({ children }) => (
        <ExperimentProvider value={{ getExperiment: () => ({ test: 13 }), getExperimentChanges$: () => EMPTY }}>
          {children}
        </ExperimentProvider>
      );
      const { result } = renderHook(() => useExperiment("connector.orderOverwrite", { test: 10 }), { wrapper });
      expect(result.current).toEqual({ test: 13 });
    });

    it("should return the defaultValue if ExperimentService provides undefined", () => {
      const wrapper: React.FC = ({ children }) => (
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        <ExperimentProvider value={{ getExperiment: () => undefined as any, getExperimentChanges$: () => EMPTY }}>
          {children}
        </ExperimentProvider>
      );
      const { result } = renderHook(() => useExperiment("connector.orderOverwrite", { test: 10 }), { wrapper });
      expect(result.current).toEqual({ test: 10 });
    });

    it("should return the default value if no ExperimentService is provided", () => {
      const { result } = renderHook(() => useExperiment("connector.orderOverwrite", { test: 42 }));
      expect(result.current).toEqual({ test: 42 });
    });

    it("should rerender whenever the ExperimentService emits a new value", () => {
      const subject = new Subject<Experiments["connector.orderOverwrite"]>();
      const wrapper: React.FC = ({ children }) => (
        <ExperimentProvider
          value={{ getExperiment: () => ({ test: 13 }), getExperimentChanges$: () => subject.asObservable() }}
        >
          {children}
        </ExperimentProvider>
      );
      const { result } = renderHook(() => useExperiment("connector.orderOverwrite", { test: 10 }), {
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
