import { FormikErrors, getIn } from "formik";
import isEqual from "lodash/isEqual";
import React, { memo, useCallback, useMemo } from "react";
import { useToggle } from "react-use";

import { DropDownOptionDataItem } from "components/ui/DropDown";

import { SyncSchemaField, SyncSchemaFieldObject, SyncSchemaStream } from "core/domain/catalog";
import { traverseSchemaToField } from "core/domain/catalog/traverseSchemaToField";
import {
  AirbyteStreamConfiguration,
  DestinationSyncMode,
  NamespaceDefinitionType,
  SyncMode,
  SelectedFieldInfo,
} from "core/request/AirbyteClient";
import { useDestinationNamespace } from "hooks/connection/useDestinationNamespace";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { equal, naturalComparatorBy } from "utils/objects";
import { ConnectionFormValues, SUPPORTED_MODES } from "views/Connection/ConnectionForm/formConfig";

import styles from "./CatalogSection.module.scss";
import { CatalogTreeTableRow } from "./next/CatalogTreeTableRow";
import { StreamDetailsPanel } from "./next/StreamDetailsPanel/StreamDetailsPanel";
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
  const isNewStreamsTableEnabled = process.env.REACT_APP_NEW_STREAMS_TABLE ?? false;

  const {
    destDefinitionSpecification: { supportedDestinationSyncModes },
  } = useConnectionFormService();
  const { mode } = useConnectionFormService();

  const [isRowExpanded, onExpand] = useToggle(false);
  const { stream, config } = streamNode;

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
      let newPrimaryKey: string[][];

      if (config?.primaryKey?.find((pk) => equal(pk, pkPath))) {
        newPrimaryKey = config.primaryKey.filter((key) => !equal(key, pkPath));
      } else {
        newPrimaryKey = [...(config?.primaryKey ?? []), pkPath];
      }

      updateStreamWithConfig({ primaryKey: newPrimaryKey });
    },
    [config?.primaryKey, updateStreamWithConfig]
  );

  const onCursorSelect = useCallback(
    (cursorField: string[]) => updateStreamWithConfig({ cursorField }),
    [updateStreamWithConfig]
  );

  const onPkUpdate = useCallback(
    (newPrimaryKey: string[][]) => updateStreamWithConfig({ primaryKey: newPrimaryKey }),
    [updateStreamWithConfig]
  );

  const numberOfFieldsInStream = Object.keys(streamNode?.stream?.jsonSchema?.properties).length ?? 0;

  const onSelectedFieldsUpdate = (fieldPath: string[], isSelected: boolean) => {
    const previouslySelectedFields = config?.selectedFields || [];

    if (!config?.fieldSelectionEnabled && !isSelected) {
      // All fields in a stream are implicitly selected. When deselecting the first one, we also need to explicitly select the rest.
      const allOtherFields = fields.filter((field: SyncSchemaField) => !isEqual(field.path, fieldPath)) ?? [];
      const selectedFields: SelectedFieldInfo[] = allOtherFields.map((field) => ({ fieldPath: field.path }));
      updateStreamWithConfig({
        selectedFields,
        fieldSelectionEnabled: true,
      });
    } else if (isSelected && previouslySelectedFields.length === numberOfFieldsInStream - 1) {
      // In this case we are selecting the only unselected field
      updateStreamWithConfig({
        selectedFields: [],
        fieldSelectionEnabled: false,
      });
    } else if (isSelected) {
      updateStreamWithConfig({
        selectedFields: [...previouslySelectedFields, { fieldPath }],
        fieldSelectionEnabled: true,
      });
    } else {
      updateStreamWithConfig({
        selectedFields: previouslySelectedFields.filter((f) => !isEqual(f.fieldPath, fieldPath)) || [],
        fieldSelectionEnabled: true,
      });
    }
  };

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

  const fields = useMemo(() => {
    const traversedFields = traverseSchemaToField(stream?.jsonSchema, stream?.name);

    return traversedFields.sort(naturalComparatorBy((field) => field.cleanedName));
  }, [stream?.jsonSchema, stream?.name]);

  const flattenedFields = useMemo(() => flatten(fields), [fields]);

  const primitiveFields = useMemo<SyncSchemaField[]>(
    () => flattenedFields.filter(SyncSchemaFieldObject.isPrimitive),
    [flattenedFields]
  );

  const destName = prefix + (streamNode.stream?.name ?? "");
  const configErrors = getIn(
    errors,
    isNewStreamsTableEnabled
      ? `syncCatalog.streams[${streamNode.id}].config`
      : `schema.streams[${streamNode.id}].config`
  );
  const hasError = configErrors && Object.keys(configErrors).length > 0;
  const pkType = getPathType(pkRequired, shouldDefinePk);
  const cursorType = getPathType(cursorRequired, shouldDefineCursor);
  const hasFields = fields?.length > 0;
  const disabled = mode === "readonly";

  const StreamComponent = isNewStreamsTableEnabled ? CatalogTreeTableRow : StreamHeader;

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
        (isNewStreamsTableEnabled ? (
          <StreamDetailsPanel
            config={config}
            disabled={mode === "readonly"}
            syncSchemaFields={flattenedFields}
            onClose={onExpand}
            onCursorSelect={onCursorSelect}
            onPkSelect={onPkSelect}
            onSelectedChange={onSelectStream}
            shouldDefinePk={shouldDefinePk}
            shouldDefineCursor={shouldDefineCursor}
            isCursorDefinitionSupported={cursorRequired}
            isPKDefinitionSupported={pkRequired}
            stream={stream}
          />
        ) : (
          <div className={styles.streamFieldTableContainer}>
            <StreamFieldTable
              config={config}
              syncSchemaFields={flattenedFields}
              onCursorSelect={onCursorSelect}
              onPkSelect={onPkSelect}
              handleFieldToggle={onSelectedFieldsUpdate}
              shouldDefinePk={shouldDefinePk}
              shouldDefineCursor={shouldDefineCursor}
            />
          </div>
        ))}
    </div>
  );
};

export const CatalogSection = memo(CatalogSectionInner);
