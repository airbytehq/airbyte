import React, { memo, useCallback, useMemo } from "react";
import { useToggle } from "react-use";
import { useIntl } from "react-intl";
import styled from "styled-components";
import { FormikErrors, getIn } from "formik";

import {
  AirbyteStream,
  AirbyteStreamConfiguration,
  DestinationSyncMode,
  SyncMode,
  SyncSchemaField,
  SyncSchemaFieldObject,
  SyncSchemaStream,
} from "core/domain/catalog";
import { traverseSchemaToField } from "core/domain/catalog/fieldUtil";
import { DropDownRow } from "components";
import { TreeRowWrapper } from "./components/TreeRowWrapper";
import { Rows } from "./components/Rows";

import { ConnectionFormValues, SUPPORTED_MODES } from "../../formConfig";
import { StreamHeader } from "./StreamHeader";
import { FieldHeader } from "./FieldHeader";
import { FieldRow } from "./FieldRow";

import { equal, naturalComparatorBy } from "utils/objects";

const Section = styled.div<{ error?: boolean }>`
  border: 1px solid
    ${(props) => (props.error ? props.theme.dangerColor : "none")};
`;

type TreeViewRowProps = {
  streamNode: SyncSchemaStream;
  errors: FormikErrors<ConnectionFormValues>;
  destinationSupportedSyncModes: DestinationSyncMode[];
  updateStream: (
    stream: AirbyteStream,
    newConfiguration: Partial<AirbyteStreamConfiguration>
  ) => void;
};

const CatalogSectionInner: React.FC<TreeViewRowProps> = ({
  streamNode,
  updateStream,
  errors,
  destinationSupportedSyncModes,
}) => {
  const formatMessage = useIntl().formatMessage;
  const [isRowExpanded, onExpand] = useToggle(false);
  const { stream, config } = streamNode;
  const streamId = stream.name;

  const updateStreamWithConfig = useCallback(
    (config: Partial<AirbyteStreamConfiguration>) =>
      updateStream(stream, config),
    [updateStream, stream]
  );

  const onSelectSyncMode = useCallback(
    (
      data: DropDownRow.IDataItem & {
        rawValue: {
          syncMode: SyncMode;
          destinationSyncMode: DestinationSyncMode;
        };
      }
    ) => updateStreamWithConfig(data.rawValue),
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
    (field: SyncSchemaField) => {
      const pkPath = field.name.split(".");

      let newPrimaryKey: string[][];

      if (pkPaths.has(field.name)) {
        newPrimaryKey = config.primaryKey.filter((key) => !equal(key, pkPath));
      } else {
        newPrimaryKey = [...config.primaryKey, pkPath];
      }

      updateStreamWithConfig({ primaryKey: newPrimaryKey });
    },
    [config.primaryKey, pkPaths, updateStreamWithConfig]
  );

  const onCursorSelect = useCallback(
    (field: SyncSchemaField) => {
      const cursorPath = field.name.split(".");

      updateStreamWithConfig({ cursorField: cursorPath });
    },
    [updateStreamWithConfig]
  );

  const pkRequired =
    config.destinationSyncMode === DestinationSyncMode.Dedupted;
  const cursorRequired = config.syncMode === SyncMode.Incremental;
  const showPkControl =
    stream.sourceDefinedPrimaryKey.length === 0 && pkRequired;
  const showCursorControl = !stream.sourceDefinedCursor && cursorRequired;

  const selectedCursorPath = config.cursorField.join(".");

  const fields = useMemo(() => {
    const traversedFields = traverseSchemaToField(stream.jsonSchema, streamId);

    return traversedFields.sort(
      naturalComparatorBy((field) => field.cleanedName)
    );
  }, [stream, streamId]);

  const availableSyncModes = useMemo(
    () =>
      SUPPORTED_MODES.filter(
        ([syncMode, destinationSyncMode]) =>
          stream.supportedSyncModes.includes(syncMode) &&
          destinationSupportedSyncModes.includes(destinationSyncMode)
      ).map(([syncMode, destinationSyncMode]) => ({
        value: `${syncMode}.${destinationSyncMode}`,
        rawValue: { syncMode, destinationSyncMode },
        text: formatMessage(
          {
            id: "connection.stream.syncMode",
            defaultMessage: `${syncMode}.${destinationSyncMode}`,
          },
          {
            syncMode: formatMessage({
              id: `syncMode.${syncMode}`,
              defaultMessage: syncMode,
            }),
            destinationSyncMode: formatMessage({
              id: `destinationSyncMode.${destinationSyncMode}`,
              defaultMessage: destinationSyncMode,
            }),
          }
        ),
      })),
    [stream.supportedSyncModes, destinationSupportedSyncModes, formatMessage]
  );

  const hasChildren = fields && fields.length > 0;

  const configErrors = getIn(errors, `schema.streams[${streamNode.id}].config`);
  const hasError = configErrors && Object.keys(configErrors).length > 0;

  return (
    <Section error={hasError}>
      <TreeRowWrapper>
        <StreamHeader
          stream={streamNode}
          destName={""}
          destNamespace={""}
          availableSyncModes={availableSyncModes}
          syncMode={`${config.syncMode}.${config.destinationSyncMode}`}
          onSelectStream={onSelectStream}
          onSelectSyncMode={onSelectSyncMode}
          isRowExpanded={isRowExpanded}
          hasFields={hasChildren}
          onExpand={onExpand}
        />
      </TreeRowWrapper>
      {isRowExpanded && hasChildren && (
        <>
          <TreeRowWrapper depth={1}>
            <FieldHeader />
          </TreeRowWrapper>
          <Rows fields={fields}>
            {(field) => (
              <TreeRowWrapper depth={1}>
                <FieldRow
                  name={field.name}
                  type={field.type}
                  destinationName={""}
                  isCursor={field.name === selectedCursorPath}
                  isPrimaryKey={pkPaths.has(field.name)}
                  isPrimaryKeyEnabled={
                    showPkControl && SyncSchemaFieldObject.isPrimitive(field)
                  }
                  isCursorEnabled={
                    showCursorControl &&
                    SyncSchemaFieldObject.isPrimitive(field)
                  }
                  onPrimaryKeyChange={() => onPkSelect(field)}
                  onCursorChange={() => onCursorSelect(field)}
                />
              </TreeRowWrapper>
            )}
          </Rows>
        </>
      )}
    </Section>
  );
};

const CatalogSection = memo(CatalogSectionInner);

export { CatalogSection };
