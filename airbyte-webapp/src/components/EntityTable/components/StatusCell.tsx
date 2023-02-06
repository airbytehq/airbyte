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
  schemaChange?: SchemaChange;
}

export const StatusCell: React.FC<StatusCellProps> = ({
  enabled,
  isManual,
  id,
  isSyncing,
  allowSync,
  schemaChange,
  hasBreakingChange,
}) => {
  const allowAutoDetectSchema = useFeature(FeatureItem.AllowAutoDetectSchema);

  return (
    <div className={styles.container} data-testid={`statusCell-${id}`}>
      <StatusCellControl
        enabled={enabled}
        id={id}
        isSyncing={isSyncing}
        isManual={isManual}
        hasBreakingChange={hasBreakingChange}
        allowSync={allowSync}
      />
      {allowAutoDetectSchema && <ChangesStatusIcon schemaChange={schemaChange} />}
    </div>
  );
};
