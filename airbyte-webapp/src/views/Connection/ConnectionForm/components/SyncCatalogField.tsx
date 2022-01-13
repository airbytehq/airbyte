import React, { useCallback, useMemo, useState } from "react";
import { FieldProps, setIn } from "formik";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import type { DestinationSyncMode } from "core/domain/catalog";
import { SyncSchemaStream } from "core/domain/catalog";

import { CheckBox, LabeledRadioButton } from "components";
import { Cell, Header } from "components/SimpleTableComponents";
import CatalogTree from "views/Connection/CatalogTree";
import Search from "./Search";
import { naturalComparatorBy } from "utils/objects";
import { SyncCatalogFilters } from "./SyncCatalogFilters";

const TreeViewContainer = styled.div`
  margin-bottom: 29px;
  border-radius: 4px;
  max-height: 600px;
  overflow-y: auto;
  --webkit-overlay: true;
  // Find better way (for checkbox)
  margin-left: -43px;
  padding-left: 43px;
  width: calc(100% + 43px);
`;

const SchemaHeader = styled(Header)`
  min-height: 33px;
`;

const SubtitleCell = styled(Cell).attrs(() => ({ lighter: true }))`
  font-size: 10px;
  line-height: 12px;
  border-top: 1px solid ${({ theme }) => theme.greyColor0};
  padding-top: 5px;
`;

const CheckboxCell = styled(Cell)`
  max-width: 43px;
  text-align: center;
  margin-left: -43px;
`;

const StreamsContent = styled.div`
  margin-left: 43px;
`;

const ClearSubtitleCell = styled(SubtitleCell)`
  border-top: none;
`;

const FiltersContent = styled.div`
  margin: 6px 0 21px;
  display: flex;
`;

const RadioButtonControl = styled(LabeledRadioButton)`
  margin: 0 0 0 5px;
`;

const HeaderBlock = styled.div`
  margin: 10px 0 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-direction: row;
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
`;

type SchemaViewProps = {
  additionalControl?: React.ReactNode;
  destinationSupportedSyncModes: DestinationSyncMode[];
} & FieldProps<SyncSchemaStream[]>;

const SyncCatalogField: React.FC<SchemaViewProps> = ({
  destinationSupportedSyncModes,
  additionalControl,
  field,
  form,
}) => {
  const { value: streams, name: fieldName } = field;

  const [searchString, setSearchString] = useState("");
  const [filterMode, setFilterMode] = useState(SyncCatalogFilters.All);

  const setField = form.setFieldValue;

  const onChangeSchema = useCallback(
    (newValue: SyncSchemaStream[]) => setField(fieldName, newValue),
    [fieldName, setField]
  );

  const onChangeStream = useCallback(
    (newValue: SyncSchemaStream) =>
      onChangeSchema(
        streams.map((str) => (str.id === newValue.id ? newValue : str))
      ),
    [streams, onChangeSchema]
  );

  const sortedSchema = useMemo(
    () =>
      streams.sort(naturalComparatorBy((syncStream) => syncStream.stream.name)),
    [streams]
  );

  const filteredStreams = useMemo(() => {
    const filters: Array<(s: SyncSchemaStream) => boolean> = [
      (_: SyncSchemaStream) => true,
      searchString
        ? (stream: SyncSchemaStream) =>
            stream.stream.name
              .toLowerCase()
              .includes(searchString.toLowerCase())
        : null,
      filterMode !== SyncCatalogFilters.All
        ? (stream: SyncSchemaStream) =>
            (filterMode === SyncCatalogFilters.Selected &&
              stream.config.selected) ||
            (filterMode === SyncCatalogFilters.NotSelected &&
              !stream.config.selected)
        : null,
    ].filter(Boolean) as Array<(s: SyncSchemaStream) => boolean>;

    return sortedSchema.filter((stream) => filters.every((f) => f(stream)));
  }, [searchString, filterMode, sortedSchema]);

  const hasSelectedItem = useMemo(
    () => filteredStreams.some((streamNode) => streamNode.config.selected),
    [filteredStreams]
  );

  const onCheckAll = useCallback(() => {
    const allSelectedValues = !hasSelectedItem;

    const newSchema = filteredStreams.map((streamNode) =>
      setIn(streamNode, "config.selected", allSelectedValues)
    );

    onChangeSchema(newSchema);
  }, [hasSelectedItem, onChangeSchema, filteredStreams]);

  return (
    <>
      <HeaderBlock>
        <FormattedMessage id="form.dataSync" />
        {additionalControl}
      </HeaderBlock>
      <Search onSearch={setSearchString} />
      <FiltersContent>
        <RadioButtonControl
          onChange={(value) => {
            setFilterMode(value.target.value as SyncCatalogFilters);
          }}
          name="FilterAll"
          value={SyncCatalogFilters.All}
          checked={filterMode === SyncCatalogFilters.All}
          label={<FormattedMessage id="form.all" />}
        />
        <RadioButtonControl
          onChange={(value) => {
            setFilterMode(value.target.value as SyncCatalogFilters);
          }}
          name="FilterSelected"
          value={SyncCatalogFilters.Selected}
          checked={filterMode === SyncCatalogFilters.Selected}
          label={<FormattedMessage id="form.selected" />}
        />
        <RadioButtonControl
          onChange={(value) => {
            setFilterMode(value.target.value as SyncCatalogFilters);
          }}
          name="FilterNotSelected"
          value={SyncCatalogFilters.NotSelected}
          checked={filterMode === SyncCatalogFilters.NotSelected}
          label={<FormattedMessage id="form.notSelected" />}
        />
      </FiltersContent>
      <StreamsContent>
        <SchemaHeader>
          <CheckboxCell>
            <CheckBox onChange={onCheckAll} checked={hasSelectedItem} />
          </CheckboxCell>
          <Cell lighter flex={0.5}>
            <FormattedMessage id="sources.sync" />
          </Cell>
          <Cell lighter>
            <FormattedMessage id="sources.source" />
          </Cell>
          <Cell />
          <Cell lighter flex={1.5}>
            <FormattedMessage id="form.syncMode" />
          </Cell>
          <Cell lighter>
            <FormattedMessage id="form.cursorField" />
          </Cell>
          <Cell lighter>
            <FormattedMessage id="form.primaryKey" />
          </Cell>
          <Cell lighter>
            <FormattedMessage id="connector.destination" />
          </Cell>
          <Cell />
        </SchemaHeader>
        <SchemaHeader>
          <CheckboxCell />
          <ClearSubtitleCell flex={0.5} />
          <SubtitleCell>
            <FormattedMessage id="form.namespace" />
          </SubtitleCell>
          <SubtitleCell>
            <FormattedMessage id="form.streamName" />
          </SubtitleCell>
          <SubtitleCell flex={1.5}>
            <FormattedMessage id="form.sourceAndDestination" />
          </SubtitleCell>
          <ClearSubtitleCell />
          <ClearSubtitleCell />
          <SubtitleCell>
            <FormattedMessage id="form.namespace" />
          </SubtitleCell>
          <SubtitleCell>
            <FormattedMessage id="form.streamName" />
          </SubtitleCell>
        </SchemaHeader>
        <TreeViewContainer>
          <CatalogTree
            streams={filteredStreams}
            onChangeStream={onChangeStream}
            destinationSupportedSyncModes={destinationSupportedSyncModes}
          />
        </TreeViewContainer>
      </StreamsContent>
    </>
  );
};

export default React.memo(SyncCatalogField);
