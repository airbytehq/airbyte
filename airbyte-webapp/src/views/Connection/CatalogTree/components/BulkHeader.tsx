import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import intersection from "lodash/intersection";

import { Button, Cell, Header, Toggle } from "components";
import { SyncSettingsDropdown } from "./SyncSettingsDropdown";
import { SUPPORTED_MODES } from "../../ConnectionForm/formConfig";
import { useBulkEdit } from "hooks/services/BulkEdit/BulkEditService";
import {
  DestinationSyncMode,
  SyncMode,
  SyncSchemaField,
  SyncSchemaFieldObject,
  SyncSchemaStream,
  traverseSchemaToField,
} from "core/domain/catalog";
import { flatten } from "../utils";
import { pathDisplayName, PathPopout } from "./PathPopout";
import { ArrowCell, CheckboxCell, HeaderCell } from "../styles";

const ActionCell = styled.div`
  display: flex;
`;

const SchemaHeader = styled(Header)`
  min-height: 41px;
  height: 41px;
  background: ${({ theme }) => theme.primaryColor};
  border-radius: 8px 8px 0 0;
`;

const ActionButton = styled(Button).attrs({
  type: "button",
})`
  white-space: nowrap;
`;

type BulkHeaderProps = {};

function calculateSharedFields(selectedBatchNodes: SyncSchemaStream[]) {
  const primitiveFieldsByStream = selectedBatchNodes.map(({ stream }) => {
    const traversedFields = traverseSchemaToField(
      stream.jsonSchema,
      stream.name
    );
    const flattenedFields = flatten(traversedFields);

    return flattenedFields.filter(SyncSchemaFieldObject.isPrimitive);
  });

  const pathMap = new Map<string, SyncSchemaField>();

  // calculate intersection of primitive fields across all selected streams
  primitiveFieldsByStream.forEach((fields, index) => {
    if (index === 0) {
      fields.forEach((field) =>
        pathMap.set(pathDisplayName(field.path), field)
      );
    } else {
      const fieldMap = new Set(fields.map((f) => pathDisplayName(f.path)));
      pathMap.forEach((_, k) => (!fieldMap.has(k) ? pathMap.delete(k) : null));
    }
  });

  return Array.from(pathMap.values());
}

export const BulkHeader: React.FC<BulkHeaderProps> = () => {
  const {
    selectedBatchNodes,
    // TODO: extract this from context
    destinationSupportedSyncModes,
    options,
    onChangeOption,
    onApply,
    isActive,
    onCancel,
  } = useBulkEdit();

  const availableSyncModes = useMemo(
    () =>
      SUPPORTED_MODES.filter(([syncMode, destinationSyncMode]) => {
        const supportableModes = intersection(
          selectedBatchNodes.flatMap((n) => n.stream.supportedSyncModes)
        );
        return (
          supportableModes.includes(syncMode) &&
          destinationSupportedSyncModes.includes(destinationSyncMode)
        );
      }).map(([syncMode, destinationSyncMode]) => ({
        value: { syncMode, destinationSyncMode },
      })),
    [selectedBatchNodes, destinationSupportedSyncModes]
  );

  const primitiveFields: SyncSchemaField[] = useMemo(
    () => calculateSharedFields(selectedBatchNodes),
    [selectedBatchNodes]
  );

  if (!isActive) {
    return null;
  }

  // TODO: calculate actualy type
  const pkType = "required";
  const cursorType = "required";
  const pkRequired =
    options.destinationSyncMode === DestinationSyncMode.Dedupted;
  const cursorRequired = options.syncMode === SyncMode.Incremental;
  // const shouldDefinePk =
  //   stream.sourceDefinedPrimaryKey.length === 0 && pkRequired;
  // const shouldDefineCursor = !stream.sourceDefinedCursor && cursorRequired;

  const paths = primitiveFields.map((f) => f.path);

  return (
    <SchemaHeader>
      <CheckboxCell />
      <ArrowCell />
      <HeaderCell flex={0.4}>
        <Toggle
          small
          checked={options.selected}
          onChange={() => onChangeOption({ selected: !options.selected })}
        />
      </HeaderCell>
      <HeaderCell />
      <HeaderCell />
      <Cell flex={1.5}>
        <SyncSettingsDropdown
          value={{
            syncMode: options.syncMode,
            destinationSyncMode: options.destinationSyncMode,
          }}
          options={availableSyncModes}
          onChange={({ value }) => onChangeOption({ ...value })}
        />
      </Cell>
      <HeaderCell>
        {cursorRequired && (
          <PathPopout
            isMulti={false}
            onPathChange={(path) => onChangeOption({ cursorField: path })}
            pathType={cursorType}
            paths={paths}
            path={options.cursorField}
          />
        )}
      </HeaderCell>
      <HeaderCell>
        {pkRequired && (
          <PathPopout
            isMulti={true}
            onPathChange={(path) => onChangeOption({ primaryKey: path })}
            pathType={pkType}
            paths={paths}
            path={options.primaryKey}
          />
        )}
      </HeaderCell>
      <HeaderCell />
      <HeaderCell>
        <ActionCell>
          <ActionButton onClick={onCancel}>
            <FormattedMessage id="connectionForm.bulkEdit.cancel" />
          </ActionButton>
          <ActionButton onClick={onApply}>
            <FormattedMessage id="connectionForm.bulkEdit.apply" />
          </ActionButton>
        </ActionCell>
      </HeaderCell>
    </SchemaHeader>
  );
};
