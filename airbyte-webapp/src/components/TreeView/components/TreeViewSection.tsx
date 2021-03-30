import React, { useCallback, useMemo } from "react";
import { useSet } from "react-use";
import { useIntl } from "react-intl";
import styled from "styled-components";

import {
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

const supportedModes: [SyncMode, DestinationSyncMode][] = [
  [SyncMode.FullRefresh, DestinationSyncMode.Overwrite],
  [SyncMode.FullRefresh, DestinationSyncMode.Append],
  [SyncMode.Incremental, DestinationSyncMode.Append],
  [SyncMode.Incremental, DestinationSyncMode.Dedupted],
];

type TreeViewRowProps = {
  isChild?: boolean;
  streamNode: SyncSchemaStream;
  updateItem: (
    streamId: string,
    newConfiguration: Partial<AirbyteStreamConfiguration>
  ) => void;
};

const TreeViewSection: React.FC<TreeViewRowProps> = ({
  streamNode,
  updateItem,
}) => {
  const formatMessage = useIntl().formatMessage;
  const { stream, config } = streamNode;
  const streamId = stream.name;

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
      updateItem(streamId, { syncMode, destinationSyncMode });
    },
    [streamId, updateItem]
  );

  const onCheckBoxClick = useCallback(
    () =>
      updateItem(streamId, {
        selected: !config.selected,
      }),
    [streamId, config, updateItem]
  );

  const fullData = useMemo(
    () =>
      supportedModes
        .filter(([syncMode]) => stream.supportedSyncModes.includes(syncMode))
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
    [stream.supportedSyncModes, formatMessage]
  );

  const pkPaths = useMemo(
    () =>
      new Set(
        config.primaryKey.map((pkPath) => `${stream.name}.${pkPath.join(".")}`)
      ),
    [config, stream]
  );

  const onPkSelect = (field: SyncSchemaField) => {
    const pkPath = field.name.replace(`${stream.name}.`, "").split(".");

    if (pkPaths.has(field.name)) {
      updateItem(streamId, {
        primaryKey: config.primaryKey.filter((key) => !equal(key, pkPath)),
      });
    } else {
      updateItem(streamId, { primaryKey: [...config.primaryKey, pkPath] });
    }
  };

  const selectedCursorPath = `${stream.name}.${config.cursorField.join(".")}`;

  const onCursorSelect = (field: SyncSchemaField) => {
    const cursorPath = field.name.replace(`${stream.name}.`, "").split(".");

    updateItem(streamId, { cursorField: cursorPath });
  };

  const hasChildren = fields && fields.length > 0;

  const hasPk = config.destinationSyncMode === DestinationSyncMode.Dedupted;
  const hasCursor = config.syncMode === SyncMode.Incremental;
  const showPk = stream.sourceDefinedPrimaryKey.length === 0;
  const showCursor = !stream.sourceDefinedCursor;

  const pkKeyItems = config.primaryKey.map((k) => k.join("."));

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
        <Cell />
        <OverflowCell title={config.aliasName}>{config.aliasName}</OverflowCell>
        <Cell>
          {hasPk && (
            <ExpandFieldCell
              onExpand={onExpand}
              isItemOpen={isRowExpanded}
              tooltipItems={pkKeyItems}
            >
              {pkKeyItems.join(",")}
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
              <Cell />
            </TreeRowWrapper>
          )}
        </Rows>
      )}
    </>
  );
};

export { TreeViewSection };
