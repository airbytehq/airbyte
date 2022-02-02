import React, { useMemo } from "react";

import styled from "styled-components";
import intersection from "lodash/intersection";

// import { DestinationSyncMode, SyncMode } from "core/domain/catalog";
import { Button, Cell, Header, Toggle } from "components";
import { SyncSettingsDropdown } from "./components/SyncSettingsCell";
import { SUPPORTED_MODES } from "../ConnectionForm/formConfig";
import { useBulkEdit } from "../ConnectionForm/BulkEditService";

const HeaderCell = styled(Cell)`
  font-size: 10px;
  line-height: 13px;
`;

const CheckboxCell = styled(HeaderCell)`
  max-width: 43px;
  text-align: center;
  margin-left: -43px;
`;

const ArrowCell = styled(HeaderCell)`
  max-width: 40px;
  width: 40px;
`;

const SchemaHeader = styled(Header)`
  min-height: 41px;
  background: ${({ theme }) => theme.primaryColor};
  border-radius: 8px;
`;

const Flex = styled.div`
  display: flex;
`;

type BulkHeaderProps = {};

export const BulkHeader: React.FC<BulkHeaderProps> = ({}) => {
  //
  // const dropdownFields = primitiveFields.map((field) => ({
  //   value: field.path,
  //   label: field.path.join("."),
  // }));

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

  if (!isActive) {
    return null;
  }

  return (
    <SchemaHeader>
      <CheckboxCell></CheckboxCell>
      <ArrowCell></ArrowCell>
      <HeaderCell flex={0.4}>
        <Toggle
          small
          checked={options.selected}
          onChange={() => onChangeOption({ selected: !options.selected })}
        />
      </HeaderCell>
      <HeaderCell ellipsis></HeaderCell>
      <HeaderCell ellipsis></HeaderCell>
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
        {/*{cursorType === "required" ? (*/}
        {/*  <Popout*/}
        {/*    options={dropdownFields}*/}
        {/*    value={cursorField}*/}
        {/*    placeholder={*/}
        {/*      <FormattedMessage id="connectionForm.cursor.searchPlaceholder" />*/}
        {/*    }*/}
        {/*    onChange={(op) => onCursorChange(op.value)}*/}
        {/*    targetComponent={({ onOpen }) => (*/}
        {/*      <div onClick={onOpen}>*/}
        {/*        {stream.config.cursorField.join(".")}*/}
        {/*        <Arrow icon={faSortDown} />*/}
        {/*        <Tooltip items={stream.config.cursorField} />*/}
        {/*      </div>*/}
        {/*    )}*/}
        {/*  />*/}
        {/*) : cursorType === "sourceDefined" ? (*/}
        {/*  "<sourceDefined>"*/}
        {/*) : null}*/}
      </HeaderCell>
      <HeaderCell ellipsis></HeaderCell>
      <HeaderCell ellipsis title={"test"}></HeaderCell>
      <HeaderCell ellipsis title={"Stream name"}>
        <Flex>
          <Button type="button" onClick={onCancel}>
            cancel
          </Button>
          <Button type="button" secondary onClick={onApply}>
            apply
          </Button>
        </Flex>
      </HeaderCell>
    </SchemaHeader>
  );
};
