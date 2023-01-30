import { FormikErrors, getIn } from "formik";
import React, { memo, useCallback, useMemo } from "react";
import { useToggle } from "react-use";

import { ConnectionFormValues, SUPPORTED_MODES } from "components/connection/ConnectionForm/formConfig";
import { DropDownOptionDataItem } from "components/ui/DropDown";

import { SyncSchemaField, SyncSchemaFieldObject, SyncSchemaStream } from "core/domain/catalog";
import { traverseSchemaToField } from "core/domain/catalog/traverseSchemaToField";
import {
  AirbyteStreamConfiguration,
  DestinationSyncMode,
  NamespaceDefinitionType,
  SyncMode,
} from "core/request/AirbyteClient";
import { useDestinationNamespace } from "hooks/connection/useDestinationNamespace";
import { useNewTableDesignExperiment } from "hooks/connection/useNewTableDesignExperiment";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { naturalComparatorBy } from "utils/objects";

import styles from "./CatalogSection.module.scss";
import { CatalogTreeTableRow } from "./next/CatalogTreeTableRow";
import { StreamDetailsPanel } from "./next/StreamDetailsPanel/StreamDetailsPanel";
import {
  updatePrimaryKey,
  toggleFieldInPrimaryKey,
  updateCursorField,
  updateFieldSelected,
  toggleAllFieldsSelected,
} from "./streamConfigHelpers/streamConfigHelpers";
import { StreamFieldTable } from "./StreamFieldTable";
import { StreamHeader } from "./StreamHeader";
import { flatten, getPathType } from "./utils";

interface CatalogSectionInnerProps {
  streamNode: SyncSchemaStream;
  errors: FormikErrors<ConnectionFormValues>;
  namespaceDefinition: NamespaceDefinitionType;
  namespaceFormat: string;
  prefix: string;
  updateStream: (id: string | undefined, newConfiguration: Partial<AirbyteStreamConfiguration>) => void;
  changedSelected: boolean;
}

const CatalogSectionInner: React.FC<CatalogSectionInnerProps> = ({
  streamNode,
  updateStream,
  namespaceDefinition,
  namespaceFormat,
  prefix,
  errors,
  changedSelected,
}) => {
  const { stream, config } = streamNode;
  const isNewTableDesignEnabled = useNewTableDesignExperiment();

  const fields = useMemo(() => {
    const traversedFields = traverseSchemaToField(stream?.jsonSchema, stream?.name);
    return traversedFields.sort(naturalComparatorBy((field) => field.cleanedName));
  }, [stream?.jsonSchema, stream?.name]);

  const numberOfFieldsInStream = Object.keys(streamNode?.stream?.jsonSchema?.properties).length ?? 0;

  const {
    destDefinitionSpecification: { supportedDestinationSyncModes },
  } = useConnectionFormService();
  const { mode } = useConnectionFormService();

  const [isRowExpanded, onExpand] = useToggle(false);

  const updateStreamWithConfig = useCallback(
    (config: Partial<AirbyteStreamConfiguration>) => updateStream(streamNode.id, config),
    [updateStream, streamNode]
  );

  const onSelectSyncMode = useCallback(
    (data: DropDownOptionDataItem) => updateStreamWithConfig(data.value),
    [updateStreamWithConfig]
  );

  const onSelectStream = useCallback(
    () =>
      updateStreamWithConfig({
        selected: !(config && config.selected),
      }),
    [config, updateStreamWithConfig]
  );

  const onPkSelect = useCallback(
    (pkPath: string[]) => {
      if (!config) {
        return;
      }
      const updatedConfig = toggleFieldInPrimaryKey(config, pkPath, numberOfFieldsInStream);
      updateStreamWithConfig(updatedConfig);
    },
    [config, updateStreamWithConfig, numberOfFieldsInStream]
  );

  const onCursorSelect = useCallback(
    (cursorField: string[]) => {
      if (!config) {
        return;
      }
      const updatedConfig = updateCursorField(config, cursorField, numberOfFieldsInStream);
      updateStreamWithConfig(updatedConfig);
    },
    [config, numberOfFieldsInStream, updateStreamWithConfig]
  );

  const onPkUpdate = useCallback(
    (newPrimaryKey: string[][]) => {
      if (!config) {
        return;
      }
      const updatedConfig = updatePrimaryKey(config, newPrimaryKey, numberOfFieldsInStream);
      updateStreamWithConfig(updatedConfig);
    },
    [config, updateStreamWithConfig, numberOfFieldsInStream]
  );

  const onToggleAllFieldsSelected = useCallback(() => {
    if (!config) {
      return;
    }
    const updatedConfig = toggleAllFieldsSelected(config);
    updateStreamWithConfig(updatedConfig);
  }, [config, updateStreamWithConfig]);

  const onToggleFieldSelected = useCallback(
    (fieldPath: string[], isSelected: boolean) => {
      if (!config) {
        return;
      }
      const updatedConfig = updateFieldSelected({ config, fields, fieldPath, isSelected, numberOfFieldsInStream });
      updateStreamWithConfig(updatedConfig);
    },
    [config, fields, numberOfFieldsInStream, updateStreamWithConfig]
  );

  const pkRequired = config?.destinationSyncMode === DestinationSyncMode.append_dedup;
  const cursorRequired = config?.syncMode === SyncMode.incremental;
  const shouldDefinePk = stream?.sourceDefinedPrimaryKey?.length === 0 && pkRequired;
  const shouldDefineCursor = !stream?.sourceDefinedCursor && cursorRequired;

  const availableSyncModes = useMemo(
    () =>
      SUPPORTED_MODES.filter(
        ([syncMode, destinationSyncMode]) =>
          stream?.supportedSyncModes?.includes(syncMode) && supportedDestinationSyncModes?.includes(destinationSyncMode)
      ).map(([syncMode, destinationSyncMode]) => ({
        value: { syncMode, destinationSyncMode },
      })),
    [stream?.supportedSyncModes, supportedDestinationSyncModes]
  );

  const destNamespace =
    useDestinationNamespace({
      namespaceDefinition,
      namespaceFormat,
    }) ?? "";

  const flattenedFields = useMemo(() => flatten(fields), [fields]);

  const primitiveFields = useMemo<SyncSchemaField[]>(
    () => flattenedFields.filter(SyncSchemaFieldObject.isPrimitive),
    [flattenedFields]
  );

  const destName = prefix + (streamNode.stream?.name ?? "");
  const configErrors = getIn(
    errors,
    isNewTableDesignEnabled ? `syncCatalog.streams[${streamNode.id}].config` : `schema.streams[${streamNode.id}].config`
  );
  const hasError = configErrors && Object.keys(configErrors).length > 0;
  const pkType = getPathType(pkRequired, shouldDefinePk);
  const cursorType = getPathType(cursorRequired, shouldDefineCursor);
  const hasFields = fields?.length > 0;
  const disabled = mode === "readonly";

  const StreamComponent = isNewTableDesignEnabled ? CatalogTreeTableRow : StreamHeader;

  return (
    <div className={styles.catalogSection}>
      <StreamComponent
        stream={streamNode}
        destNamespace={destNamespace}
        destName={destName}
        availableSyncModes={availableSyncModes}
        onSelectStream={onSelectStream}
        onSelectSyncMode={onSelectSyncMode}
        isRowExpanded={isRowExpanded}
        primitiveFields={primitiveFields}
        pkType={pkType}
        onPrimaryKeyChange={onPkUpdate}
        cursorType={cursorType}
        onCursorChange={onCursorSelect}
        fields={fields}
        onExpand={onExpand}
        changedSelected={changedSelected}
        hasError={hasError}
        configErrors={configErrors}
        disabled={disabled}
      />
      {isRowExpanded &&
        hasFields &&
        (isNewTableDesignEnabled ? (
          <StreamDetailsPanel
            config={config}
            disabled={mode === "readonly"}
            syncSchemaFields={flattenedFields}
            onClose={onExpand}
            onCursorSelect={onCursorSelect}
            onPkSelect={onPkSelect}
            onSelectedChange={onSelectStream}
            handleFieldToggle={onToggleFieldSelected}
            shouldDefinePk={shouldDefinePk}
            shouldDefineCursor={shouldDefineCursor}
            isCursorDefinitionSupported={cursorRequired}
            isPKDefinitionSupported={pkRequired}
            stream={stream}
            toggleAllFieldsSelected={onToggleAllFieldsSelected}
          />
        ) : (
          <div className={styles.streamFieldTableContainer}>
            <StreamFieldTable
              config={config}
              syncSchemaFields={flattenedFields}
              onCursorSelect={onCursorSelect}
              onPkSelect={onPkSelect}
              handleFieldToggle={onToggleFieldSelected}
              primaryKeyIndexerType={pkType}
              cursorIndexerType={cursorType}
              shouldDefinePrimaryKey={shouldDefinePk}
              shouldDefineCursor={shouldDefineCursor}
            />
          </div>
        ))}
    </div>
  );
};

export const CatalogSection = memo(CatalogSectionInner);
