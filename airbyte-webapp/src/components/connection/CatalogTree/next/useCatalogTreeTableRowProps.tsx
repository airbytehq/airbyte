/* eslint-disable css-modules/no-unused-class */
import classNames from "classnames";
import isEqual from "lodash/isEqual";
import { useMemo } from "react";

import { PillButtonVariant } from "components/ui/PillSelect/PillButton";

import { SyncSchemaStream } from "core/domain/catalog";
import { useBulkEditSelect } from "hooks/services/BulkEdit/BulkEditService";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";

import styles from "./CatalogTreeTableRow.module.scss";

export type StatusToDisplay = "disabled" | "added" | "removed" | "changed" | "unchanged";

export const useCatalogTreeTableRowProps = (stream: SyncSchemaStream) => {
  const [isSelected] = useBulkEditSelect(stream.id);
  const { initialValues } = useConnectionFormService();

  const isStreamEnabled = stream.config?.selected;

  const statusToDisplay = useMemo<StatusToDisplay>(() => {
    const rowStatusChanged =
      initialValues.syncCatalog.streams.find(
        (item) => item.stream?.name === stream.stream?.name && item.stream?.namespace === stream.stream?.namespace
      )?.config?.selected !== stream.config?.selected;

    const rowChanged = !isEqual(
      initialValues.syncCatalog.streams.find(
        (item) =>
          item.stream &&
          stream.stream &&
          item.stream.name === stream.stream.name &&
          item.stream.namespace === stream.stream.namespace
      )?.config,
      stream.config
    );

    if (!isStreamEnabled && !rowStatusChanged) {
      return "disabled";
    } else if (rowStatusChanged) {
      return isStreamEnabled ? "added" : "removed";
    } else if (rowChanged) {
      return "changed";
    }
    return "unchanged";
  }, [initialValues.syncCatalog.streams, isStreamEnabled, stream.config, stream.stream]);

  const pillButtonVariant = useMemo<PillButtonVariant>(() => {
    if (statusToDisplay === "added" && !isSelected) {
      return "green";
    } else if (statusToDisplay === "removed" && !isSelected) {
      return "red";
    } else if (statusToDisplay === "changed" || isSelected) {
      return "blue";
    }
    return "grey";
  }, [isSelected, statusToDisplay]);

  const streamHeaderContentStyle = classNames(styles.streamHeaderContent, {
    [styles.added]: statusToDisplay === "added" && !isSelected,
    [styles.removed]: statusToDisplay === "removed" && !isSelected,
    [styles.changed]: statusToDisplay === "changed" || isSelected,
    [styles.disabled]: statusToDisplay === "disabled",
  });

  return {
    streamHeaderContentStyle,
    isSelected,
    statusToDisplay,
    pillButtonVariant,
  };
};
