import { setIn, useFormikContext } from "formik";
import React, { useContext, useEffect, useMemo, useState } from "react";
import { useSet } from "react-use";

import { SyncSchemaStream } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";

const Context = React.createContext<BulkEditServiceContext | null>(null);

export interface BulkEditServiceContext {
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
  options: Partial<AirbyteStreamConfiguration>;
  onApply: () => void;
  onCancel: () => void;
}

const defaultOptions: Partial<AirbyteStreamConfiguration> = {
  selected: false,
};

export const BulkEditServiceProvider: React.FC<
  React.PropsWithChildren<{
    nodes: SyncSchemaStream[];
    update: (streams: SyncSchemaStream[]) => void;
  }>
> = ({ children, nodes, update }) => {
  const { setStatus, status } = useFormikContext();
  const [selectedBatchNodes, { reset, toggle, add }] = useSet<string | undefined>(new Set());
  const [options, setOptions] = useState<Partial<AirbyteStreamConfiguration>>(defaultOptions);

  const isActive = selectedBatchNodes.size > 0;
  useEffect(() => {
    if (status && status.editControlsVisible !== !isActive) {
      setStatus({ ...status, editControlsVisible: !isActive });
    }
  }, [setStatus, isActive, status]);

  const resetBulk = () => {
    reset();
    setOptions(defaultOptions);
  };

  const onApply = () => {
    const updatedConfig = nodes.map((node) =>
      selectedBatchNodes.has(node.id) ? setIn(node, "config", { ...node.config, ...options }) : node
    );

    update(updatedConfig);
    resetBulk();
  };

  const onCancel = () => {
    reset();
    resetBulk();
  };
  const allChecked = selectedBatchNodes.size === nodes.length;

  const ctx: BulkEditServiceContext = {
    isActive,
    toggleNode: toggle,
    onCheckAll: () => (allChecked ? reset() : nodes.forEach((n) => add(n.id))),
    allChecked,
    selectedBatchNodeIds: Array.from(selectedBatchNodes).filter((node): node is string => node !== undefined),
    selectedBatchNodes: nodes.filter((n) => selectedBatchNodes.has(n.id)),
    onChangeOption: (newOptions) => setOptions({ ...options, ...newOptions }),
    options,
    onApply,
    onCancel,
  };

  return <Context.Provider value={ctx}>{children}</Context.Provider>;
};

export const useBulkEditService = (): BulkEditServiceContext => {
  const ctx = useContext(Context);

  if (!ctx) {
    throw new Error("useBulkEdit should be used within BatchEditProvider");
  }

  return ctx;
};

export const useBulkEditSelect = (id: string | undefined): [boolean, () => void] => {
  const { selectedBatchNodeIds, toggleNode } = useBulkEditService();
  const isIncluded = id !== undefined && selectedBatchNodeIds.includes(id);

  return useMemo(() => [isIncluded, () => toggleNode(id)], [isIncluded, toggleNode, id]);
};
