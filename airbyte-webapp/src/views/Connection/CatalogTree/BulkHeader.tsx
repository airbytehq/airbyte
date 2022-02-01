import React from "react";

import styled from "styled-components";

// import { DestinationSyncMode, SyncMode } from "core/domain/catalog";
import { Cell, Toggle } from "components";
import { SyncSettingsCell } from "./components/SyncSettingsCell";
//
// const Arrow = styled(FontAwesomeIcon)<{ isOpen?: boolean }>`
//   color: ${({ theme }) => theme.greyColor40};
//   margin-left: 6px;
//   transform: ${({ isOpen }) => isOpen && "rotate(180deg)"};
//   transition: 0.3s;
//   vertical-align: sub;
// `;
//
// const EmptyField = styled.span`
//   color: ${({ theme }) => theme.greyColor40};
// `;

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

// type SyncSchema = {
//   syncMode: SyncMode;
//   destinationSyncMode: DestinationSyncMode;
// };

type BulkHeaderProps = {
  // stream: SyncSchemaStream;
  // destName: string;
  // destNamespace: string;
  // availableSyncModes: {
  //   value: SyncSchema;
  // }[];
  // onSelectSyncMode: (selectedMode: DropDownRow.IDataItem) => void;
  // onSelectStream: () => void;
  //
  // primitiveFields: SyncSchemaField[];
  //
  // pkType: null | "required" | "sourceDefined";
  // onPrimaryKeyChange: (pkPath: string[][]) => void;
  // cursorType: null | "required" | "sourceDefined";
  // onCursorChange: (cursorPath: string[]) => void;
  //
  // isRowExpanded: boolean;
  // hasFields: boolean;
  // onExpand: () => void;
};

export const BulkHeader: React.FC<BulkHeaderProps> = (
  {
    // stream,
    // destName,
    // destNamespace,
    // onSelectSyncMode,
    // onSelectStream,
    // availableSyncModes,
    // pkType,
    // onPrimaryKeyChange,
    // onCursorChange,
    // primitiveFields,
    // cursorType,
  }
) => {
  // const syncSchema = useMemo(
  //   () => ({
  //     syncMode,
  //     destinationSyncMode,
  //   }),
  //   [syncMode, destinationSyncMode]
  // );
  //
  // const dropdownFields = primitiveFields.map((field) => ({
  //   value: field.path,
  //   label: field.path.join("."),
  // }));

  return (
    <>
      <CheckboxCell></CheckboxCell>
      <ArrowCell></ArrowCell>
      <HeaderCell flex={0.4}>
        <Toggle small checked={false} onChange={() => ({})} />
      </HeaderCell>
      <HeaderCell ellipsis></HeaderCell>
      <HeaderCell ellipsis></HeaderCell>
      <SyncSettingsCell value={{}} options={[]} onChange={() => ({})} />
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
      <HeaderCell ellipsis>
        {/*{pkType === "required" ? (*/}
        {/*  <Popout*/}
        {/*    options={dropdownFields}*/}
        {/*    value={primaryKey}*/}
        {/*    // @ts-ignore need to solve issue with typings*/}
        {/*    isMulti={true}*/}
        {/*    isSearchable*/}
        {/*    onChange={(options: { value: string[] }[]) => {*/}
        {/*      onPrimaryKeyChange(options.map((op) => op.value));*/}
        {/*    }}*/}
        {/*    placeholder={*/}
        {/*      <FormattedMessage id="connectionForm.primaryKey.searchPlaceholder" />*/}
        {/*    }*/}
        {/*    components={PkPopupComponents}*/}
        {/*    targetComponent={({ onOpen }) => (*/}
        {/*      <div onClick={onOpen}>*/}
        {/*        {primaryKey.map((k) => k.join(".")).join(", ")}*/}
        {/*        <Arrow icon={faSortDown} />*/}
        {/*        <Tooltip items={primaryKey.map((k) => k.join("."))} />*/}
        {/*      </div>*/}
        {/*    )}*/}
        {/*  />*/}
        {/*) : pkType === "sourceDefined" ? (*/}
        {/*  "<sourceDefined>"*/}
        {/*) : null}*/}
      </HeaderCell>
      <HeaderCell ellipsis title={"test"}>
        {/*{destNamespace}*/}
      </HeaderCell>
      <HeaderCell ellipsis title={"Stream name"}>
        test
      </HeaderCell>
    </>
  );
};
