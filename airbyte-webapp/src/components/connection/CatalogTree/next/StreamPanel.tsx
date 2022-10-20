import { Dialog } from "@headlessui/react";

import { Overlay } from "components/ui/Overlay/Overlay";

import { SyncSchemaFieldObject } from "core/domain/catalog";
import { AirbyteStream } from "core/request/AirbyteClient";

import { FieldHeader } from "../FieldHeader";
import { FieldRow } from "../FieldRow";
import { pathDisplayName } from "../PathPopout";
import { StreamFieldTableProps } from "../StreamFieldTable";
import { TreeRowWrapper } from "../TreeRowWrapper";
import { StreamConnectionHeader } from "./StreamConnectionHeader";
import styles from "./StreamPanel.module.scss";
import { StreamPanelHeader } from "./StreamPanelHeader";

interface StreamPanelProps extends StreamFieldTableProps {
  disabled?: boolean;
  onClose: () => void;
  onSelectedChange: () => void;
  stream?: AirbyteStream;
}

export const StreamPanel: React.FC<StreamPanelProps> = ({
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
        <StreamConnectionHeader />
        <TreeRowWrapper noBorder>
          <FieldHeader />
        </TreeRowWrapper>
        {syncSchemaFields.map((field) => (
          <TreeRowWrapper depth={1} key={pathDisplayName(field.path)}>
            <FieldRow
              field={field}
              config={config}
              isPrimaryKeyEnabled={shouldDefinePk && SyncSchemaFieldObject.isPrimitive(field)}
              isCursorEnabled={shouldDefineCursor && SyncSchemaFieldObject.isPrimitive(field)}
              onPrimaryKeyChange={onPkSelect}
              onCursorChange={onCursorSelect}
            />
          </TreeRowWrapper>
        ))}
      </Dialog.Panel>
    </Dialog>
  );
};
