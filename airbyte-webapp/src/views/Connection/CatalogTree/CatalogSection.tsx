import React, { memo, useCallback, useMemo } from "react";
import { useToggle } from "react-use";
import styled from "styled-components";
import { FormikErrors, getIn, useField } from "formik";

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
import { DropDownRow } from "components";
import { TreeRowWrapper } from "./components/TreeRowWrapper";

import {
  ConnectionFormValues,
  SUPPORTED_MODES,
} from "views/Connection/ConnectionForm/formConfig";
import { StreamHeader } from "./StreamHeader";
import { FieldHeader } from "./FieldHeader";
import { FieldRow } from "./FieldRow";

import { equal, naturalComparatorBy } from "utils/objects";

const flatten = (
  fArr: SyncSchemaField[],
  arr: SyncSchemaField[] = []
): SyncSchemaField[] =>
  fArr.reduce<SyncSchemaField[]>((acc, f) => {
    acc.push(f);

    if (f.fields?.length) {
      return flatten(f.fields, acc);
    }
    return acc;
  }, arr);

const Section = styled.div<{ error?: boolean }>`
  border: 1px solid
    ${(props) => (props.error ? props.theme.dangerColor : "none")};
`;

const RowsContainer = styled.div<{ depth?: number }>`
  background: ${({ theme }) => theme.whiteColor5};
  border-radius: 4px;
  margin: 0
    ${({ depth = 0 }) => `${depth * 38}px ${depth * 5}px ${depth * 38}px`};
`;

type TreeViewRowProps = {
  streamNode: SyncSchemaStream;
  errors: FormikErrors<ConnectionFormValues>;
  destinationSupportedSyncModes: DestinationSyncMode[];
  updateStream: (
    id: string,
    newConfiguration: Partial<AirbyteStreamConfiguration>
  ) => void;
};

const CatalogSectionInner: React.FC<TreeViewRowProps> = ({
  streamNode,
  updateStream,
  errors,
  destinationSupportedSyncModes,
}) => {
  const [isRowExpanded, onExpand] = useToggle(false);
  const { stream, config } = streamNode;
  const streamId = stream.name;

  const updateStreamWithConfig = useCallback(
    (config: Partial<AirbyteStreamConfiguration>) =>
      updateStream(streamNode.id, config),
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

  const pkPaths = useMemo(
    () => new Set(config.primaryKey.map((pkPath) => pkPath.join("."))),
    [config.primaryKey]
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
    (cursorPath: string[]) =>
      updateStreamWithConfig({ cursorField: cursorPath }),
    [updateStreamWithConfig]
  );

  const pkRequired =
    config.destinationSyncMode === DestinationSyncMode.Dedupted;
  const cursorRequired = config.syncMode === SyncMode.Incremental;
  const showPkControl =
    stream.sourceDefinedPrimaryKey.length === 0 && pkRequired;
  const showCursorControl = !stream.sourceDefinedCursor && cursorRequired;

  const selectedCursorPath = config.cursorField.join(".");

  const availableSyncModes = useMemo(
    () =>
      SUPPORTED_MODES.filter(
        ([syncMode, destinationSyncMode]) =>
          stream.supportedSyncModes.includes(syncMode) &&
          destinationSupportedSyncModes.includes(destinationSyncMode)
      ).map(([syncMode, destinationSyncMode]) => ({
        value: { syncMode, destinationSyncMode },
      })),
    [stream.supportedSyncModes, destinationSupportedSyncModes]
  );

  const configErrors = getIn(errors, `schema.streams[${streamNode.id}].config`);
  const hasError = configErrors && Object.keys(configErrors).length > 0;

  const [{ value: namespaceDefinition }] = useField("namespaceDefinition");
  const [{ value: namespaceFormat }] = useField("namespaceFormat");
  const [{ value: prefix }] = useField("prefix");
  const destNamespace = getDestinationNamespace({
    namespaceDefinition,
    namespaceFormat,
    sourceNamespace: stream.namespace,
  });

  const fields = useMemo(() => {
    const traversedFields = traverseSchemaToField(stream.jsonSchema, streamId);

    return traversedFields.sort(
      naturalComparatorBy((field) => field.cleanedName)
    );
  }, [stream.jsonSchema, streamId]);

  const hasChildren = fields && fields.length > 0;

  const flattenedFields = useMemo(() => flatten(fields), [fields]);

  const primitiveFieldNames = useMemo(
    () =>
      flattenedFields
        .filter(SyncSchemaFieldObject.isPrimitive)
        .map((field) => field.name),
    [flattenedFields]
  );

  return (
    <Section error={hasError}>
      <TreeRowWrapper>
        <StreamHeader
          stream={streamNode}
          destNamespace={destNamespace}
          destName={prefix + streamNode.stream.name}
          availableSyncModes={availableSyncModes}
          onSelectStream={onSelectStream}
          onSelectSyncMode={onSelectSyncMode}
          isRowExpanded={isRowExpanded}
          primitiveFields={primitiveFieldNames}
          pkType={
            pkRequired ? (showPkControl ? "required" : "sourceDefined") : null
          }
          onPrimaryKeyChange={(newPrimaryKey) =>
            updateStreamWithConfig({ primaryKey: newPrimaryKey })
          }
          cursorType={
            cursorRequired
              ? showCursorControl
                ? "required"
                : "sourceDefined"
              : null
          }
          onCursorChange={onCursorSelect}
          hasFields={hasChildren}
          onExpand={onExpand}
        />
      </TreeRowWrapper>
      {isRowExpanded && hasChildren && (
        <>
          <TreeRowWrapper noBorder>
            <FieldHeader depth={1} />
          </TreeRowWrapper>
          <RowsContainer depth={1}>
            {flattenedFields.map((field) => (
              <TreeRowWrapper depth={1} key={field.name}>
                <FieldRow
                  depth={1}
                  name={field.name}
                  type={field.type}
                  destinationName={field.cleanedName}
                  isCursor={field.name === selectedCursorPath}
                  isPrimaryKey={pkPaths.has(field.name)}
                  isPrimaryKeyEnabled={
                    showPkControl && SyncSchemaFieldObject.isPrimitive(field)
                  }
                  isCursorEnabled={
                    showCursorControl &&
                    SyncSchemaFieldObject.isPrimitive(field)
                  }
                  onPrimaryKeyChange={onPkSelect}
                  onCursorChange={onCursorSelect}
                />
              </TreeRowWrapper>
            ))}
          </RowsContainer>
        </>
      )}
    </Section>
  );
};

const CatalogSection = memo(CatalogSectionInner);

export { CatalogSection };
