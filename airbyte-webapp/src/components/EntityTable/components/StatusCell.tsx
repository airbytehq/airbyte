import React from "react";

import { SchemaChange } from "core/request/AirbyteClient";
import { FeatureItem, useFeature } from "hooks/services/Feature";

import { ChangesStatusIcon } from "./ChangesStatusIcon";
import styles from "./StatusCell.module.scss";
import { StatusCellControl } from "./StatusCellControl";

interface StatusCellProps {
  allowSync?: boolean;
  hasBreakingChange?: boolean;
  enabled?: boolean;
  isSyncing?: boolean;
  isManual?: boolean;
  id: string;
  onSync: (id: string) => void;
  schemaChange?: SchemaChange;
}

export const StatusCell: React.FC<StatusCellProps> = ({
  enabled,
  isManual,
  id,
  isSyncing,
  onSync,
  allowSync,
  schemaChange,
  hasBreakingChange,
}) => {
  const allowAutoDetectSchema = useFeature(FeatureItem.AllowAutoDetectSchema);

  return (
    <div className={styles.container}>
      <StatusCellControl
        enabled={enabled}
        id={id}
        isSyncing={isSyncing}
        isManual={isManual}
        onSync={onSync}
        hasBreakingChange={hasBreakingChange}
        allowSync={allowSync}
      />
      {allowAutoDetectSchema && <ChangesStatusIcon schemaChange={schemaChange} />}
    </div>
  );
};
