import { setIn } from "formik";
import React, { useContext, useMemo, useState, useEffect } from "react";
import { useSet } from "react-use";

import { SyncSchemaStream } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";

const Context = React.createContext<BatchContext | null>(null);

interface BatchContext {
  isActive: boolean;
  toggleNode: (id: string | undefined) => void;
  onCheckAll: () => void;
  allChecked: boolean;
  selectedBatchNodes: SyncSchemaStream[];
  selectedBatchNodeIds: string[];
  onChangeOption: (
    value:
      | ((prevState: Partial<AirbyteStreamConfiguration>) => Partial<AirbyteStreamConfiguration>)
      | Partial<AirbyteStreamConfiguration>
  ) => void;
  onChangeBulkSwitch: (
    value:
      | ((prevState: Partial<AirbyteStreamConfiguration>) => Partial<AirbyteStreamConfiguration>)
      | Partial<AirbyteStreamConfiguration>
  ) => void;
  options: Partial<AirbyteStreamConfiguration>;
  onApply: () => void;
  onCancel: () => void;
}

const defaultOptions: Partial<AirbyteStreamConfiguration> = {
  selected: false,
};

const BatchEditProvider: React.FC<{
  nodes: SyncSchemaStream[];
  update: (streams: SyncSchemaStream[]) => void;
}> = ({ children, nodes, update }) => {
  const [selectedBatchNodes, { reset, toggle, add }] = useSet<string | undefined>(new Set());
  const [options, setOptions] = useState<Partial<AirbyteStreamConfiguration>>(defaultOptions);

  useEffect(() => {
    // TODO: Monitor the value change of Stream table Switch, and update the options.selected value in time
    if (selectedBatchNodes.size > 0) {
      const selectedNodes: SyncSchemaStream[] = nodes.filter((n) => selectedBatchNodes.has(n.id) && n.config?.selected);
      if (selectedNodes.length === nodes.length) {
        setOptions({ selected: true });
      } else {
        setOptions(defaultOptions);
      }
    }
  }, [selectedBatchNodes, nodes, options.selected]);

  const resetBulk = () => {
    reset();
    // setOptions(defaultOptions);
  };

  const onApply = () => {
    const updatedConfig = nodes.map((node) =>
      selectedBatchNodes.has(node.id)
        ? options.syncMode && node.stream?.supportedSyncModes?.includes(options.syncMode)
          ? setIn(node, "config", { ...node.config, ...options, selected: node.config?.selected })
          : setIn(node, "config", { ...node.config, selected: node.config?.selected })
        : node
    );

    update(updatedConfig);
    resetBulk();
  };

  const onCancel = () => {
    reset();
    resetBulk();
  };

  const onChangeBulkSwitch = (
    newOptions:
      | ((prevState: Partial<AirbyteStreamConfiguration>) => Partial<AirbyteStreamConfiguration>)
      | Partial<AirbyteStreamConfiguration>
  ) => {
    setOptions({ ...options, ...newOptions });
    const updatedConfig = nodes.map((node) =>
      selectedBatchNodes.has(node.id) ? setIn(node, "config", { ...node.config, ...newOptions }) : node
    );

    update(updatedConfig);
    // resetBulk();
  };

  const isActive = selectedBatchNodes.size > 0;
  const allChecked = selectedBatchNodes.size === nodes.length;

  const ctx: BatchContext = {
    isActive,
    toggleNode: toggle,
    onCheckAll: () => (allChecked ? reset() : nodes.forEach((n) => add(n.id))),
    allChecked,
    selectedBatchNodeIds: Array.from(selectedBatchNodes).filter((node): node is string => node !== undefined),
    selectedBatchNodes: nodes.filter((n) => selectedBatchNodes.has(n.id)),
    onChangeOption: (newOptions) => setOptions({ ...options, ...newOptions }),
    onChangeBulkSwitch,
    options,
    onApply,
    onCancel,
  };

  return <Context.Provider value={ctx}>{children}</Context.Provider>;
};

const useBulkEdit = (): BatchContext => {
  const ctx = useContext(Context);

  if (!ctx) {
    throw new Error("useBulkEdit should be used within BatchEditProvider");
  }

  return ctx;
};

const useBulkEditSelect = (id: string | undefined): [boolean, () => void] => {
  const { selectedBatchNodeIds, toggleNode } = useBulkEdit();
  const isIncluded = id !== undefined && selectedBatchNodeIds.includes(id);

  return useMemo(() => [isIncluded, () => toggleNode(id)], [isIncluded, toggleNode, id]);
};

export type { BatchContext };
export { useBulkEditSelect, useBulkEdit, BatchEditProvider };
