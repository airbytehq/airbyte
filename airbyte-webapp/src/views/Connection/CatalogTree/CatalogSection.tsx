import { FormikErrors, getIn } from "formik";
import React, { memo, useCallback, useMemo } from "react";
import { useToggle } from "react-use";
import styled from "styled-components";

import { DropDownRow } from "components";

import {
  AirbyteStreamConfiguration,
  DestinationSyncMode,
  getDestinationNamespace,
  SyncMode,
  SyncSchemaField,
  SyncSchemaFieldObject,
  SyncSchemaStream,
} from "core/domain/catalog";
import { traverseSchemaToField } from "core/domain/catalog/fieldUtil";
import { ConnectionNamespaceDefinition } from "core/domain/connection";
import { useBulkEditSelect } from "hooks/services/BulkEdit/BulkEditService";
import { equal, naturalComparatorBy } from "utils/objects";
import { ConnectionFormValues, SUPPORTED_MODES } from "views/Connection/ConnectionForm/formConfig";

import { TreeRowWrapper } from "./components/TreeRowWrapper";
import { StreamFieldTable } from "./StreamFieldTable";
import { StreamHeader } from "./StreamHeader";
import { flatten, getPathType } from "./utils";

const Section = styled.div<{ error?: boolean; isSelected: boolean }>`
  border: 1px solid ${(props) => (props.error ? props.theme.dangerColor : "none")};
  background: ${({ theme, isSelected }) => (isSelected ? "rgba(97, 94, 255, 0.1);" : theme.greyColor0)};

  &:first-child {
    border-radius: 8px 8px 0 0;
  }

  &:last-child {
    border-radius: 0 0 8px 8px;
  }
`;

type TreeViewRowProps = {
  streamNode: SyncSchemaStream;
  errors: FormikErrors<ConnectionFormValues>;
  destinationSupportedSyncModes: DestinationSyncMode[];
  namespaceDefinition: ConnectionNamespaceDefinition;
  namespaceFormat: string;
  prefix: string;
  updateStream: (id: string, newConfiguration: Partial<AirbyteStreamConfiguration>) => void;
};

const CatalogSectionInner: React.FC<TreeViewRowProps> = ({
  streamNode,
  updateStream,
  namespaceDefinition,
  namespaceFormat,
  prefix,
  errors,
  destinationSupportedSyncModes,
}) => {
  const [isRowExpanded, onExpand] = useToggle(false);
  const { stream, config } = streamNode;

  const [isSelected] = useBulkEditSelect(streamNode.id);

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
        selected: !config.selected,
      }),
    [config, updateStreamWithConfig]
  );

  const onPkSelect = useCallback(
    (pkPath: string[]) => {
      let newPrimaryKey: string[][];

      if (config.primaryKey.find((pk) => equal(pk, pkPath))) {
        newPrimaryKey = config.primaryKey.filter((key) => !equal(key, pkPath));
      } else {
        newPrimaryKey = [...config.primaryKey, pkPath];
      }

      updateStreamWithConfig({ primaryKey: newPrimaryKey });
    },
    [config.primaryKey, updateStreamWithConfig]
  );

  const onCursorSelect = useCallback(
    (cursorField: string[]) => updateStreamWithConfig({ cursorField }),
    [updateStreamWithConfig]
  );

  const onPkUpdate = useCallback(
    (newPrimaryKey: string[][]) => updateStreamWithConfig({ primaryKey: newPrimaryKey }),
    [updateStreamWithConfig]
  );

  const pkRequired = config.destinationSyncMode === DestinationSyncMode.Dedupted;
  const cursorRequired = config.syncMode === SyncMode.Incremental;
  const shouldDefinePk = stream.sourceDefinedPrimaryKey.length === 0 && pkRequired;
  const shouldDefineCursor = !stream.sourceDefinedCursor && cursorRequired;

  const availableSyncModes = useMemo(
    () =>
      SUPPORTED_MODES.filter(
        ([syncMode, destinationSyncMode]) =>
          stream.supportedSyncModes.includes(syncMode) && destinationSupportedSyncModes.includes(destinationSyncMode)
      ).map(([syncMode, destinationSyncMode]) => ({
        value: { syncMode, destinationSyncMode },
      })),
    [stream.supportedSyncModes, destinationSupportedSyncModes]
  );

  const destNamespace = getDestinationNamespace({
    namespaceDefinition,
    namespaceFormat,
    sourceNamespace: stream.namespace,
  });

  const fields = useMemo(() => {
    const traversedFields = traverseSchemaToField(stream.jsonSchema, stream.name);

    return traversedFields.sort(naturalComparatorBy((field) => field.cleanedName));
  }, [stream.jsonSchema, stream.name]);

  const flattenedFields = useMemo(() => flatten(fields), [fields]);

  const primitiveFields = useMemo<SyncSchemaField[]>(
    () => flattenedFields.filter(SyncSchemaFieldObject.isPrimitive),
    [flattenedFields]
  );

  const configErrors = getIn(errors, `schema.streams[${streamNode.id}].config`);
  const hasError = configErrors && Object.keys(configErrors).length > 0;
  const hasChildren = fields && fields.length > 0;

  return (
    <Section error={hasError} isSelected={isSelected}>
      <TreeRowWrapper>
        <StreamHeader
          stream={streamNode}
          destNamespace={destNamespace}
          destName={prefix + streamNode.stream.name}
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
        />
      </TreeRowWrapper>
      {isRowExpanded && hasChildren && (
        <StreamFieldTable
          config={config}
          syncSchemaFields={flattenedFields}
          onCursorSelect={onCursorSelect}
          onPkSelect={onPkSelect}
          shouldDefinePk={shouldDefinePk}
          shouldDefineCursor={shouldDefineCursor}
        />
      )}
    </Section>
  );
};

export const CatalogSection = memo(CatalogSectionInner);
