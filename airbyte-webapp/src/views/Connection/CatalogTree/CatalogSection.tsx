import { FormikErrors, getIn } from "formik";
import React, { memo, useCallback, useMemo } from "react";
import { useToggle } from "react-use";

import { DropDownRow } from "components";

import { getDestinationNamespace, SyncSchemaField, SyncSchemaFieldObject, SyncSchemaStream } from "core/domain/catalog";
import { traverseSchemaToField } from "core/domain/catalog/fieldUtil";
import { equal, naturalComparatorBy } from "utils/objects";
import { ConnectionFormValues, SUPPORTED_MODES } from "views/Connection/ConnectionForm/formConfig";

import {
  AirbyteStreamConfiguration,
  DestinationSyncMode,
  NamespaceDefinitionType,
  SyncMode,
} from "../../../core/request/AirbyteClient";
import { ConnectionFormMode } from "../ConnectionForm/ConnectionForm";
import styles from "./CatalogSection.module.scss";
import { StreamFieldTable } from "./StreamFieldTable";
import { StreamHeader } from "./StreamHeader";
import { flatten, getPathType } from "./utils";

interface CatalogSectionInnerProps {
  streamNode: SyncSchemaStream;
  errors: FormikErrors<ConnectionFormValues>;
  destinationSupportedSyncModes: DestinationSyncMode[];
  namespaceDefinition: NamespaceDefinitionType;
  namespaceFormat: string;
  prefix: string;
  updateStream: (id: string | undefined, newConfiguration: Partial<AirbyteStreamConfiguration>) => void;
  mode?: ConnectionFormMode;
  changedSelected: boolean;
}

const CatalogSectionInner: React.FC<CatalogSectionInnerProps> = ({
  streamNode,
  updateStream,
  namespaceDefinition,
  namespaceFormat,
  prefix,
  errors,
  destinationSupportedSyncModes,
  mode,
  changedSelected,
}) => {
  const [isRowExpanded, onExpand] = useToggle(false);
  const { stream, config } = streamNode;

  const updateStreamWithConfig = useCallback(
    (config: Partial<AirbyteStreamConfiguration>) => updateStream(streamNode.id, config),
    [updateStream, streamNode]
  );

  const onSelectSyncMode = useCallback(
    (data: DropDownRow.IDataItem) => updateStreamWithConfig(data.value),
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

  const pkRequired = config?.destinationSyncMode === DestinationSyncMode.append_dedup;
  const cursorRequired = config?.syncMode === SyncMode.incremental;
  const shouldDefinePk = stream?.sourceDefinedPrimaryKey?.length === 0 && pkRequired;
  const shouldDefineCursor = !stream?.sourceDefinedCursor && cursorRequired;

  const availableSyncModes = useMemo(
    () =>
      SUPPORTED_MODES.filter(
        ([syncMode, destinationSyncMode]) =>
          stream?.supportedSyncModes?.includes(syncMode) && destinationSupportedSyncModes.includes(destinationSyncMode)
      ).map(([syncMode, destinationSyncMode]) => ({
        value: { syncMode, destinationSyncMode },
      })),
    [stream?.supportedSyncModes, destinationSupportedSyncModes]
  );

  const destNamespace = getDestinationNamespace({
    namespaceDefinition,
    namespaceFormat,
    sourceNamespace: stream?.namespace,
  });

  const fields = useMemo(() => {
    const traversedFields = traverseSchemaToField(stream?.jsonSchema, stream?.name);

    return traversedFields.sort(naturalComparatorBy((field) => field.cleanedName));
  }, [stream?.jsonSchema, stream?.name]);

  const flattenedFields = useMemo(() => flatten(fields), [fields]);

  const primitiveFields = useMemo<SyncSchemaField[]>(
    () => flattenedFields.filter(SyncSchemaFieldObject.isPrimitive),
    [flattenedFields]
  );

  const configErrors = getIn(errors, `schema.streams[${streamNode.id}].config`);
  const hasError = configErrors && Object.keys(configErrors).length > 0;
  const hasChildren = fields && fields.length > 0;

  return (
    <div className={styles.catalogSection}>
      <StreamHeader
        stream={streamNode}
        destNamespace={destNamespace}
        destName={prefix + (streamNode.stream?.name ?? "")}
        availableSyncModes={availableSyncModes}
        onSelectStream={onSelectStream}
        onSelectSyncMode={onSelectSyncMode}
        isRowExpanded={isRowExpanded}
        primitiveFields={primitiveFields}
        pkType={getPathType(pkRequired, shouldDefinePk)}
        onPrimaryKeyChange={onPkUpdate}
        cursorType={getPathType(cursorRequired, shouldDefineCursor)}
        onCursorChange={onCursorSelect}
        hasFields={hasChildren}
        onExpand={onExpand}
        mode={mode}
        changedSelected={changedSelected}
        hasError={hasError}
      />
      {isRowExpanded && hasChildren && (
        <div className={styles.streamFieldTableContainer}>
          <StreamFieldTable
            config={config}
            syncSchemaFields={flattenedFields}
            onCursorSelect={onCursorSelect}
            onPkSelect={onPkSelect}
            shouldDefinePk={shouldDefinePk}
            shouldDefineCursor={shouldDefineCursor}
          />
        </div>
      )}
    </div>
  );
};

export const CatalogSection = memo(CatalogSectionInner);
