import React, { useContext, useMemo, useState } from "react";
import { useSet } from "react-use";
import { setIn } from "formik";

import {
  AirbyteStreamConfiguration,
  DestinationSyncMode,
  SyncSchemaStream,
} from "core/domain/catalog";

const Context = React.createContext<BatchContext>({} as any);

export interface BatchContext {
  isActive: boolean;
  selectNode: (id: string) => void;
  selectedBatchNodes: SyncSchemaStream[];
  selectedBatchNodeIds: string[];
  onChangeOption: (
    value:
      | ((
          prevState: Partial<AirbyteStreamConfiguration>
        ) => Partial<AirbyteStreamConfiguration>)
      | Partial<AirbyteStreamConfiguration>
  ) => void;
  destinationSupportedSyncModes: DestinationSyncMode[];
  options: Partial<AirbyteStreamConfiguration>;
  onApply: () => void;
  onCancel: () => void;
}

export const BatchEditProvider: React.FC<{
  nodes: SyncSchemaStream[];
  update: (streams: SyncSchemaStream[]) => void;
  destinationSupportedSyncModes: DestinationSyncMode[];
}> = ({ children, nodes, destinationSupportedSyncModes, update }) => {
  const [selectedBatchNodes, { reset, toggle }] = useSet<string>(new Set());
  const [options, setOptions] = useState<Partial<AirbyteStreamConfiguration>>(
    {}
  );

  const onApply = () => {
    const updatedConfig = nodes.map((node) =>
      selectedBatchNodes.has(node.id)
        ? setIn(node, "config", { ...node.config, ...options })
        : node
    );

    update(updatedConfig);
    reset();
  };

  const onCancel = () => {
    reset();
  };

  const ctx: BatchContext = {
    destinationSupportedSyncModes,
    isActive: selectedBatchNodes.size > 0,
    selectNode: toggle,
    selectedBatchNodeIds: Array.from(selectedBatchNodes),
    selectedBatchNodes: nodes.filter((n) => selectedBatchNodes.has(n.id)),
    onChangeOption: (newOptions) => setOptions({ ...options, ...newOptions }),
    options,
    onApply,
    onCancel,
  };

  return <Context.Provider value={ctx}>{children}</Context.Provider>;
};
const useBulkEdit = () => {
  const ctx = useContext(Context);

  return ctx;
};
const useBulkEditSelect = (id: string): [boolean, () => void] => {
  const { selectedBatchNodeIds, selectNode } = useBulkEdit();
  const isIncluded = selectedBatchNodeIds.includes(id);

  return useMemo(() => [isIncluded, () => selectNode(id)], [
    isIncluded,
    selectNode,
    id,
  ]);
};
export { useBulkEditSelect };
export { useBulkEdit };
