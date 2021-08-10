import React, { memo, useCallback, useMemo } from "react";
import { useToggle } from "react-use";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import { getIn, FormikErrors } from "formik";

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
import { RadioButton, CheckBox, DropDownRow } from "components";

import { MainInfoCell } from "./components/MainInfoCell";
import { SyncSettingsCell } from "./components/SyncSettingsCell";
import { ExpandFieldCell } from "./components/ExpandFieldCell";
import { OverflowCell } from "./components/OverflowCell";
import { TreeRowWrapper } from "./components/TreeRowWrapper";
import { Rows } from "./components/Rows";

import { equal, naturalComparatorBy } from "utils/objects";
import { ConnectionFormValues, SUPPORTED_MODES } from "../../formConfig";

const StyledRadioButton = styled(RadioButton)`
  vertical-align: middle;
`;

const EmptyField = styled.span`
  color: ${({ theme }) => theme.greyColor40};
`;

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
    ) => {
      updateStreamWithConfig(data.rawValue);
    },
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

  const pkKeyItems = config.primaryKey.map((k) => k.join("."));
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
        <MainInfoCell
          label={stream.name}
          onCheckBoxClick={onSelectStream}
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
          {pkRequired && (
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
          {cursorRequired && (
            <ExpandFieldCell onExpand={onExpand} isItemOpen={isRowExpanded}>
              {config.cursorField.join(".")}
            </ExpandFieldCell>
          )}
        </Cell>
        <SyncSettingsCell
          value={`${config.syncMode}.${config.destinationSyncMode}`}
          data={availableSyncModes}
          onSelect={onSelectSyncMode}
        />
      </TreeRowWrapper>
      {isRowExpanded && hasChildren && (
        <Rows fields={fields} depth={1}>
          {(field, depth) => (
            <TreeRowWrapper depth={0}>
              {/*// TODO hack for v0.2.0: don't allow checking any of the children aka fields in a stream.*/}
              {/*// hideCheckbox={true} should be removed once it's possible to select these again.*/}
              {/*// https://airbytehq.slack.com/archives/C01CWUQT7UJ/p1603173180066800*/}
              <MainInfoCell
                hideCheckbox={true}
                label={field.name}
                depth={depth}
              />
              <Cell />
              <OverflowCell>{field.type}</OverflowCell>
              <OverflowCell title={field.cleanedName}>
                {field.cleanedName}
              </OverflowCell>
              <OverflowCell>
                {showPkControl && SyncSchemaFieldObject.isPrimitive(field) && (
                  <CheckBox
                    checked={pkPaths.has(field.name)}
                    onClick={() => onPkSelect(field)}
                  />
                )}
              </OverflowCell>
              <Cell>
                {showCursorControl &&
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
    </Section>
  );
};

const CatalogSection = memo(CatalogSectionInner);

export { CatalogSection };
