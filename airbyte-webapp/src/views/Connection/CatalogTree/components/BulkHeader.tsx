import intersection from "lodash/intersection";
import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button, Cell, Header, Switch } from "components";

import { SyncSchemaField, SyncSchemaFieldObject, SyncSchemaStream, traverseSchemaToField } from "core/domain/catalog";
import { DestinationSyncMode, SyncMode } from "core/request/AirbyteClient";
import { useBulkEdit } from "hooks/services/BulkEdit/BulkEditService";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";

import { SUPPORTED_MODES } from "../../ConnectionForm/formConfig";
import { ArrowCell, CheckboxCell, HeaderCell } from "../styles";
import { flatten, getPathType } from "../utils";
import styles from "./BulkHeader.module.scss";
import { pathDisplayName, PathPopout } from "./PathPopout";
import { SyncSettingsDropdown } from "./SyncSettingsDropdown";

const ActionCell = styled.div`
  display: flex;
`;

const SchemaHeader = styled(Header)`
  min-height: 41px;
  height: 41px;
  background: ${({ theme }) => theme.primaryColor};
  border-radius: 8px 8px 0 0;
`;

function calculateSharedFields(selectedBatchNodes: SyncSchemaStream[]) {
  const primitiveFieldsByStream = selectedBatchNodes.map(({ stream }) => {
    const traversedFields = traverseSchemaToField(stream?.jsonSchema, stream?.name);
    const flattenedFields = flatten(traversedFields);

    return flattenedFields.filter(SyncSchemaFieldObject.isPrimitive);
  });

  const pathMap = new Map<string, SyncSchemaField>();

  // calculate intersection of primitive fields across all selected streams
  primitiveFieldsByStream.forEach((fields, index) => {
    if (index === 0) {
      fields.forEach((field) => pathMap.set(pathDisplayName(field.path), field));
    } else {
      const fieldMap = new Set(fields.map((f) => pathDisplayName(f.path)));
      pathMap.forEach((_, k) => (!fieldMap.has(k) ? pathMap.delete(k) : null));
    }
  });

  return Array.from(pathMap.values());
}

export const BulkHeader: React.FC = () => {
  const {
    destDefinition: { supportedDestinationSyncModes },
  } = useConnectionFormService();
  const { selectedBatchNodes, options, onChangeOption, onApply, isActive, onCancel } = useBulkEdit();

  const availableSyncModes = useMemo(
    () =>
      SUPPORTED_MODES.filter(([syncMode, destinationSyncMode]) => {
        const supportableModes = intersection(selectedBatchNodes.flatMap((n) => n.stream?.supportedSyncModes));
        return supportableModes.includes(syncMode) && supportedDestinationSyncModes?.includes(destinationSyncMode);
      }).map(([syncMode, destinationSyncMode]) => ({
        value: { syncMode, destinationSyncMode },
      })),
    [selectedBatchNodes, supportedDestinationSyncModes]
  );

  const primitiveFields: SyncSchemaField[] = useMemo(
    () => calculateSharedFields(selectedBatchNodes),
    [selectedBatchNodes]
  );

  if (!isActive) {
    return null;
  }

  const pkRequired = options.destinationSyncMode === DestinationSyncMode.append_dedup;
  const shouldDefinePk = selectedBatchNodes.every((n) => n.stream?.sourceDefinedPrimaryKey?.length === 0) && pkRequired;
  const cursorRequired = options.syncMode === SyncMode.incremental;
  const shouldDefineCursor = selectedBatchNodes.every((n) => !n.stream?.sourceDefinedCursor) && cursorRequired;

  const pkType = getPathType(pkRequired, shouldDefinePk);
  const cursorType = getPathType(cursorRequired, shouldDefineCursor);

  const paths = primitiveFields.map((f) => f.path);

  return (
    <SchemaHeader>
      <CheckboxCell />
      <ArrowCell />
      <HeaderCell flex={0.4}>
        <Switch small checked={options.selected} onChange={() => onChangeOption({ selected: !options.selected })} />
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
        {cursorType && (
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
        {pkType && (
          <PathPopout
            isMulti
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
          <Button className={styles.actionButton} onClick={onCancel}>
            <FormattedMessage id="connectionForm.bulkEdit.cancel" />
          </Button>
          <Button className={styles.actionButton} onClick={onApply}>
            <FormattedMessage id="connectionForm.bulkEdit.apply" />
          </Button>
        </ActionCell>
      </HeaderCell>
    </SchemaHeader>
  );
};
