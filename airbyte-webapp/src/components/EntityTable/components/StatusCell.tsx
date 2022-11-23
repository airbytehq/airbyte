import React from "react";

import { SchemaChange } from "core/request/AirbyteClient";

import { ChangesStatusIcon } from "./ChangesStatusIcon";
import styles from "./StatusCell.module.scss";
import { StatusCellControl } from "./StatusCellControl";

interface IProps {
  allowSync?: boolean;
  enabled?: boolean;
  isSyncing?: boolean;
  isManual?: boolean;
  id: string;
  onSync: (id: string) => void;
  schemaChange: SchemaChange;
}

export const StatusCell: React.FC<IProps> = ({ enabled, isManual, id, isSyncing, onSync, allowSync, schemaChange }) => {
  return (
    <div className={styles.container}>
      <StatusCellControl
        enabled={enabled}
        id={id}
        isSyncing={isSyncing}
        isManual={isManual}
        onSync={onSync}
        allowSync={allowSync}
      />
      <ChangesStatusIcon schemaChange={schemaChange} />
    </div>
  );
};
