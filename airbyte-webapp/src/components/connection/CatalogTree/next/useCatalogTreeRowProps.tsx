/* eslint-disable css-modules/no-unused-class */
import { faMinus, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { useField } from "formik";
import { isEqual } from "lodash";
import { useMemo } from "react";

import { ModificationIcon } from "components/icons/ModificationIcon";
import { PillButtonVariant } from "components/ui/PillSelect/PillButton";

import { SyncSchemaStream } from "core/domain/catalog";
import { useBulkEditSelect } from "hooks/services/BulkEdit/BulkEditService";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";

import styles from "./CatalogTreeTableRow.module.scss";

export const useCatalogTreeRowProps = (stream: SyncSchemaStream) => {
  const { initialValues } = useConnectionFormService();
  const [isSelected] = useBulkEditSelect(stream.id);

  const [, { error }] = useField(`schema.streams[${stream.id}].config`);

  // in case error is an empty string
  const hasError = error !== undefined;

  const isStreamEnabled = stream.config?.selected;

  const statusToDisplay = useMemo(() => {
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

    if (rowStatusChanged) {
      return isStreamEnabled ? "added" : "removed";
    } else if (rowChanged) {
      return "changed";
    } else if (!isStreamEnabled && !rowStatusChanged) {
      return "disabled";
    }
    return "unchanged";
  }, [initialValues.syncCatalog.streams, isStreamEnabled, stream.config, stream.stream]);

  const pillButtonVariant: PillButtonVariant = useMemo(() => {
    if (statusToDisplay === "added") {
      return "green";
    } else if (statusToDisplay === "removed") {
      return "red";
    } else if (statusToDisplay === "changed" || isSelected) {
      return "blue";
    }
    return "grey";
  }, [isSelected, statusToDisplay]);

  const statusIcon = useMemo(() => {
    if (statusToDisplay === "added") {
      return <FontAwesomeIcon icon={faPlus} size="2x" className={classNames(styles.icon, styles.plus)} />;
    } else if (statusToDisplay === "removed") {
      return <FontAwesomeIcon icon={faMinus} size="2x" className={classNames(styles.icon, styles.minus)} />;
    } else if (statusToDisplay === "changed") {
      return (
        <div className={classNames(styles.icon, styles.changed)}>
          <ModificationIcon color={styles.modificationIconColor} />
        </div>
      );
    }
    return null;
  }, [statusToDisplay]);

  const streamHeaderContentStyle = classNames(styles.streamHeaderContent, {
    [styles.added]: statusToDisplay === "added",
    [styles.removed]: statusToDisplay === "removed",
    [styles.changed]: statusToDisplay === "changed" || isSelected,
    [styles.disabled]: statusToDisplay === "disabled",
    [styles.error]: hasError,
  });

  return {
    streamHeaderContentStyle,
    statusIcon,
    pillButtonVariant,
  };
};
