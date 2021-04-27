import React, { useCallback, useMemo } from "react";
import { useSet } from "react-use";
import { useIntl, FormattedMessage } from "react-intl";
import styled from "styled-components";

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

import { Cell } from "components/SimpleTableComponents";
import { DropDownRow } from "components/DropDown";
import { CheckBox } from "components/CheckBox";
import { RadioButton } from "components/RadioButton";

import MainInfoCell from "./MainInfoCell";
import { SyncSettingsCell } from "./SyncSettingsCell";
import { TreeRowWrapper } from "./TreeRowWrapper";
import ExpandFieldCell from "./ExpandFieldCell";
import { OverflowCell } from "./OverflowCell";
import { equal } from "utils/objects";
import { Rows } from "./Rows";

const StyledRadioButton = styled(RadioButton)`
  vertical-align: middle;
`;

const EmptyField = styled.span`
  color: ${({ theme }) => theme.greyColor40};
`;

const supportedModes: [SyncMode, DestinationSyncMode][] = [
  [SyncMode.FullRefresh, DestinationSyncMode.Overwrite],
  [SyncMode.FullRefresh, DestinationSyncMode.Append],
  [SyncMode.Incremental, DestinationSyncMode.Append],
  [SyncMode.Incremental, DestinationSyncMode.Dedupted],
];

type TreeViewRowProps = {
  isChild?: boolean;
  streamNode: SyncSchemaStream;
  destinationSupportedSyncModes: DestinationSyncMode[];
  updateStream: (
    stream: AirbyteStream,
    newConfiguration: Partial<AirbyteStreamConfiguration>
  ) => void;
};

const TreeViewSection: React.FC<TreeViewRowProps> = ({
  streamNode,
  updateStream,
  destinationSupportedSyncModes,
}) => {
  const formatMessage = useIntl().formatMessage;
  const { stream, config } = streamNode;
  const streamId = stream.name;

  const updateStreamWithConfig = useCallback(
    (config: Partial<AirbyteStreamConfiguration>) =>
      updateStream(stream, config),
    [updateStream, stream]
  );

  const [, { has, toggle }] = useSet(new Set());
  const isRowExpanded = has(streamId);
  const onExpand = useCallback(() => toggle(streamId), [toggle, streamId]);

  const fields = useMemo(
    () => traverseSchemaToField(stream.jsonSchema, streamId),
    [stream, streamId]
  );

  const onSelectSyncMode = useCallback(
    (data: DropDownRow.IDataItem) => {
      const [syncMode, destinationSyncMode] = data.value.split(".") as [
        SyncMode,
        DestinationSyncMode
      ];
      updateStreamWithConfig({ syncMode, destinationSyncMode });
    },
    [updateStreamWithConfig]
  );

  const onCheckBoxClick = useCallback(
    () =>
      updateStreamWithConfig({
        selected: !config.selected,
      }),
    [config, updateStreamWithConfig]
  );

  const fullData = useMemo(
    () =>
      supportedModes
        .filter(
          ([syncMode, destinationSyncMode]) =>
            stream.supportedSyncModes.includes(syncMode) &&
            destinationSupportedSyncModes.includes(destinationSyncMode)
        )
        .map(([syncMode, destinationSyncMode]) => ({
          value: `${syncMode}.${destinationSyncMode}`,
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

  const pkPaths = useMemo(
    () => new Set(config.primaryKey.map((pkPath) => pkPath.join("."))),
    [config]
  );

  const onPkSelect = (field: SyncSchemaField) => {
    const pkPath = field.name.split(".");

    let newPrimaryKey: string[][];

    if (pkPaths.has(field.name)) {
      newPrimaryKey = config.primaryKey.filter((key) => !equal(key, pkPath));
    } else {
      newPrimaryKey = [...config.primaryKey, pkPath];
    }

    updateStreamWithConfig({ primaryKey: newPrimaryKey });
  };

  const onCursorSelect = (field: SyncSchemaField) => {
    const cursorPath = field.name.split(".");

    updateStreamWithConfig({ cursorField: cursorPath });
  };

  const hasChildren = fields && fields.length > 0;

  const hasPk = config.destinationSyncMode === DestinationSyncMode.Dedupted;
  const hasCursor = config.syncMode === SyncMode.Incremental;
  const showPk = stream.sourceDefinedPrimaryKey.length === 0;
  const showCursor = !stream.sourceDefinedCursor;

  const pkKeyItems = config.primaryKey.map((k) => k.join("."));
  const selectedCursorPath = config.cursorField.join(".");

  return (
    <>
      <TreeRowWrapper>
        <MainInfoCell
          label={stream.name}
          onCheckBoxClick={onCheckBoxClick}
          onExpand={onExpand}
          isItemChecked={config.selected}
          isItemHasChildren={hasChildren}
          isItemOpen={isRowExpanded}
        />
        <Cell>
          {stream.namespace || (
            <EmptyField>
              <FormattedMessage id="form.noNamespace" />
            </EmptyField>
          )}
        </Cell>
        <Cell />
        <OverflowCell title={config.aliasName}>{config.aliasName}</OverflowCell>
        <Cell>
          {hasPk && (
            <ExpandFieldCell
              onExpand={onExpand}
              isItemOpen={isRowExpanded}
              tooltipItems={pkKeyItems}
            >
              <FormattedMessage
                id="form.pkSelected"
                values={{ count: pkKeyItems.length, items: pkKeyItems }}
              />
            </ExpandFieldCell>
          )}
        </Cell>
        <Cell>
          {hasCursor && (
            <ExpandFieldCell onExpand={onExpand} isItemOpen={isRowExpanded}>
              {config.cursorField.join(".")}
            </ExpandFieldCell>
          )}
        </Cell>
        <SyncSettingsCell
          value={`${config.syncMode}.${config.destinationSyncMode}`}
          data={fullData}
          onSelect={onSelectSyncMode}
        />
      </TreeRowWrapper>
      {isRowExpanded && hasChildren && fields && (
        <Rows fields={fields} depth={1}>
          {(field, depth) => (
            <TreeRowWrapper depth={0}>
              {/*// TODO hack for v0.2.0: don't allow checking any of the children aka fields in a stream.*/}
              {/*// hideCheckbox={true} should be removed once it's possible to select these again.*/}
              {/*// https://airbytehq.slack.com/archives/C01CWUQT7UJ/p1603173180066800*/}
              <MainInfoCell
                hideCheckbox={true}
                label={field.name}
                isItemChecked={true}
                depth={depth}
              />
              <Cell />
              <OverflowCell>{field.type}</OverflowCell>
              <OverflowCell title={field.cleanedName}>
                {field.cleanedName}
              </OverflowCell>
              <OverflowCell>
                {hasPk &&
                  showPk &&
                  SyncSchemaFieldObject.isPrimitive(field) && (
                    <CheckBox
                      checked={pkPaths.has(field.name)}
                      onClick={() => onPkSelect(field)}
                    />
                  )}
              </OverflowCell>
              <Cell>
                {hasCursor &&
                  showCursor &&
                  SyncSchemaFieldObject.isPrimitive(field) && (
                    <StyledRadioButton
                      checked={field.name === selectedCursorPath}
                      onClick={() => onCursorSelect(field)}
                    />
                  )}
              </Cell>
              <Cell flex={1.5} />
            </TreeRowWrapper>
          )}
        </Rows>
      )}
    </>
  );
};

export { TreeViewSection };
