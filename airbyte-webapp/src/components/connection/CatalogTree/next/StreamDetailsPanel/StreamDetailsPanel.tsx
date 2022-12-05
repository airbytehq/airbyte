import { Dialog } from "@headlessui/react";
import React from "react";

import { Overlay } from "components/ui/Overlay";

import { AirbyteStream } from "core/request/AirbyteClient";

import styles from "./StreamDetailsPanel.module.scss";
import { StreamFieldsTable, StreamFieldsTableProps } from "./StreamFieldsTable/StreamFieldsTable";
import { StreamPanelHeader } from "./StreamPanelHeader/StreamPanelHeader";

interface StreamDetailsPanelProps extends StreamFieldsTableProps {
  disabled?: boolean;
  onClose: () => void;
  onSelectedChange: () => void;
  stream?: AirbyteStream;
}

export const StreamDetailsPanel: React.FC<StreamDetailsPanelProps> = ({
  config,
  disabled,
  onPkSelect,
  onCursorSelect,
  onClose,
  onSelectedChange,
  shouldDefinePk,
  shouldDefineCursor,
  stream,
  syncSchemaFields,
}) => {
  return (
    <Dialog className={styles.dialog} open onClose={onClose}>
      <Overlay />
      <Dialog.Panel className={styles.container}>
        <StreamPanelHeader
          stream={stream}
          config={config}
          disabled={disabled}
          onClose={onClose}
          onSelectedChange={onSelectedChange}
        />
        <div className={styles.tableContainer}>
          <StreamFieldsTable
            config={config}
            syncSchemaFields={syncSchemaFields}
            onCursorSelect={onCursorSelect}
            onPkSelect={onPkSelect}
            shouldDefinePk={shouldDefinePk}
            shouldDefineCursor={shouldDefineCursor}
          />
        </div>
      </Dialog.Panel>
    </Dialog>
  );
};
