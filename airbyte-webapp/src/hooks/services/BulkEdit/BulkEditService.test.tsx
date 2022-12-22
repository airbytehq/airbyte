import { renderHook } from "@testing-library/react-hooks";
import { Formik } from "formik";
import React from "react";
import { act } from "react-dom/test-utils";

import { SyncSchemaStream } from "../../../core/domain/catalog";
import { DestinationSyncMode, SyncMode } from "../../../core/request/AirbyteClient";
import { TestWrapper } from "../../../test-utils/testutils";
import { BulkEditServiceProvider, useBulkEditSelect, useBulkEditService } from "./BulkEditService";

const MOCK_NODES = [
  {
    id: "1",
    stream: {
      sourceDefinedCursor: true,
      defaultCursorField: ["source_cursor"],
      sourceDefinedPrimaryKey: [["new_primary_key"]],
      jsonSchema: {},
      name: "test",
      namespace: "namespace-test",
      supportedSyncModes: [],
    },
    config: {
      destinationSyncMode: DestinationSyncMode.append,
      selected: false,
      syncMode: SyncMode.full_refresh,
      cursorField: ["old_cursor"],
      primaryKey: [["old_primary_key"]],
      aliasName: "",
    },
  },
  {
    id: "2",
    stream: {
      sourceDefinedCursor: true,
      defaultCursorField: ["source_cursor"],
      sourceDefinedPrimaryKey: [["new_primary_key"]],
      jsonSchema: {},
      name: "test2",
      namespace: "namespace-test-2",
      supportedSyncModes: [],
    },
    config: {
      destinationSyncMode: DestinationSyncMode.append,
      selected: false,
      syncMode: SyncMode.full_refresh,
      cursorField: ["old_cursor"],
      primaryKey: [["old_primary_key"]],
      aliasName: "",
    },
  },
];
const mockUpdate = jest.fn();

const provider = (
  nodes: SyncSchemaStream[],
  update: (streams: SyncSchemaStream[]) => void
): React.FC<React.PropsWithChildren<unknown>> => {
  return ({ children }) => (
    <TestWrapper>
      <Formik initialValues={{}} onSubmit={async () => false} initialStatus={{ editControlsVisible: false }}>
        <BulkEditServiceProvider nodes={nodes} update={update}>
          {children}
        </BulkEditServiceProvider>
      </Formik>
    </TestWrapper>
  );
};

describe("BulkEditServiceProvider", () => {
  beforeEach(() => {
    mockUpdate.mockClear();
  });
  it("isActive should work correctly", () => {
    const wrapper = provider(MOCK_NODES, mockUpdate);
    const { result } = renderHook(() => useBulkEditService(), { wrapper });
    expect(result.current.isActive).toBe(false);
    act(() => {
      result.current.toggleNode("1");
    });
    expect(result.current.isActive).toBe(true);
  });
  it("onCheckAll and selectedBatchNodes should work correctly", () => {
    const wrapper = provider(MOCK_NODES, mockUpdate);
    const { result } = renderHook(() => useBulkEditService(), { wrapper });
    act(() => {
      result.current.onCheckAll();
    });
    expect(result.current.selectedBatchNodes).toEqual(MOCK_NODES);

    act(() => {
      result.current.onCheckAll();
    });
    expect(result.current.selectedBatchNodes).toEqual([]);

    act(() => {
      result.current.toggleNode("1");
    });
    expect(result.current.selectedBatchNodes).toEqual([MOCK_NODES[0]]);

    act(() => {
      result.current.onCheckAll();
    });
    expect(result.current.selectedBatchNodes).toEqual(MOCK_NODES);
  });
  it("allChecked should work correctly", () => {
    const wrapper = provider(MOCK_NODES, mockUpdate);
    const { result } = renderHook(() => useBulkEditService(), { wrapper });
    act(() => {
      result.current.onCheckAll();
    });
    expect(result.current.allChecked).toEqual(true);

    act(() => {
      result.current.onCheckAll();
    });
    expect(result.current.allChecked).toEqual(false);

    act(() => {
      result.current.toggleNode("1");
    });
    expect(result.current.allChecked).toEqual(false);

    act(() => {
      result.current.onCheckAll();
    });
    expect(result.current.allChecked).toEqual(true);
  });
  it("selectedBatchNodeIds should work correctly", () => {
    const wrapper = provider(MOCK_NODES, mockUpdate);
    const { result } = renderHook(() => useBulkEditService(), { wrapper });
    act(() => {
      result.current.onCheckAll();
    });
    expect(result.current.selectedBatchNodeIds).toEqual(["1", "2"]);

    act(() => {
      result.current.onCheckAll();
    });
    expect(result.current.selectedBatchNodeIds).toEqual([]);

    act(() => {
      result.current.toggleNode("1");
    });
    expect(result.current.selectedBatchNodeIds).toEqual(["1"]);

    act(() => {
      result.current.onCheckAll();
    });
    expect(result.current.selectedBatchNodeIds).toEqual(["1", "2"]);
  });
  it("options and onChangeOption should work correctly", () => {
    const wrapper = provider(MOCK_NODES, mockUpdate);
    const { result } = renderHook(() => useBulkEditService(), { wrapper });
    expect(result.current.options).toEqual({
      selected: false,
    });
    act(() => {
      result.current.onChangeOption({
        syncMode: SyncMode.full_refresh,
        aliasName: "test_1",
        primaryKey: [["test_pk"]],
      });
    });
    expect(result.current.options).toEqual({
      selected: false,
      syncMode: SyncMode.full_refresh,
      aliasName: "test_1",
      primaryKey: [["test_pk"]],
    });
  });
  it("onApply should work correctly", () => {
    const wrapper = provider(MOCK_NODES, mockUpdate);
    const { result } = renderHook(() => useBulkEditService(), { wrapper });
    act(() => {
      result.current.onChangeOption({ syncMode: SyncMode.incremental });
      result.current.toggleNode("1");
      result.current.toggleNode("2");
    });
    expect(result.current.options).toEqual({
      selected: false,
      syncMode: SyncMode.incremental,
    });
    act(() => {
      result.current.onApply();
    });
    expect(mockUpdate).toBeCalledWith([
      {
        ...MOCK_NODES[0],
        config: {
          ...MOCK_NODES[0].config,
          syncMode: SyncMode.incremental,
        },
      },
      {
        ...MOCK_NODES[1],
        config: {
          ...MOCK_NODES[1].config,
          syncMode: SyncMode.incremental,
        },
      },
    ]);
    expect(result.current.options).toEqual({ selected: false });
    expect(result.current.selectedBatchNodes).toEqual([]);
  });
  it("onCancel should work correctly", () => {
    const wrapper = provider(MOCK_NODES, mockUpdate);
    const { result } = renderHook(() => useBulkEditService(), { wrapper });
    act(() => {
      result.current.onChangeOption({ syncMode: SyncMode.incremental });
      result.current.toggleNode("1");
      result.current.toggleNode("2");
    });
    expect(result.current.options).toEqual({
      selected: false,
      syncMode: SyncMode.incremental,
    });
    act(() => {
      result.current.onCancel();
    });
    expect(result.current.options).toEqual({ selected: false });
    expect(result.current.selectedBatchNodes).toEqual([]);
  });
});

describe("useBulkEditSelect", () => {
  it("should work correctly", () => {
    const wrapper = provider(MOCK_NODES, mockUpdate);
    const { result: selectResult } = renderHook(() => useBulkEditSelect("1"), { wrapper });
    expect(selectResult.current[0]).toEqual(false);
    act(() => {
      selectResult.current[1]();
    });
    expect(selectResult.current[0]).toEqual(true);
  });
});
