import { FieldProps } from "formik";
import React, { useCallback, useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { CheckBox } from "components";
import { Cell, Header } from "components/SimpleTableComponents";

import { useConfig } from "config";
import type { DestinationSyncMode } from "core/domain/catalog";
import { SyncSchemaStream } from "core/domain/catalog";
import { BatchEditProvider, useBulkEdit } from "hooks/services/BulkEdit/BulkEditService";
import { naturalComparatorBy } from "utils/objects";
import CatalogTree from "views/Connection/CatalogTree";

import { BulkHeader } from "../../CatalogTree/components/BulkHeader";
import InformationToolTip from "./InformationToolTip";
import Search from "./Search";

const TreeViewContainer = styled.div`
  margin-bottom: 29px;
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

const ArrowCell = styled(Cell)`
  width: 40px;
  max-width: 40px;
`;

const StreamsContent = styled.div`
  margin-left: 43px;
`;

const ClearSubtitleCell = styled(SubtitleCell)`
  border-top: none;
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

const NextLineText = styled.div`
  margin-top: 10px;
`;

const LearnMoreLink = styled.a`
  opacity: 0.6;
  display: block;
  margin-top: 10px;
  color: ${({ theme }) => theme.whiteColor};
  text-decoration: none;

  &:hover {
    opacity: 0.9;
  }
`;

type SchemaViewProps = {
  additionalControl?: React.ReactNode;
  destinationSupportedSyncModes: DestinationSyncMode[];
} & FieldProps<SyncSchemaStream[]>;

const CatalogHeader: React.FC = () => {
  const config = useConfig();
  const { onCheckAll, selectedBatchNodeIds, allChecked } = useBulkEdit();

  return (
    <SchemaHeader>
      <CheckboxCell>
        <CheckBox
          onChange={onCheckAll}
          indeterminate={selectedBatchNodeIds.length > 0 && !allChecked}
          checked={allChecked}
        />
      </CheckboxCell>
      <ArrowCell />
      <Cell lighter flex={0.4}>
        <FormattedMessage id="sources.sync" />
      </Cell>
      <Cell lighter>
        <FormattedMessage id="sources.source" />
        <InformationToolTip>
          <FormattedMessage id="connectionForm.source.info" />
        </InformationToolTip>
      </Cell>
      <Cell />
      <Cell lighter flex={1.5}>
        <FormattedMessage id="form.syncMode" />
        <InformationToolTip>
          <FormattedMessage id="connectionForm.syncType.info" />
          <LearnMoreLink target="_blank" href={config.ui.syncModeLink}>
            <FormattedMessage id="form.entrypoint.docs" />
          </LearnMoreLink>
        </InformationToolTip>
      </Cell>
      <Cell lighter>
        <FormattedMessage id="form.cursorField" />
        <InformationToolTip>
          <FormattedMessage id="connectionForm.cursor.info" />
        </InformationToolTip>
      </Cell>
      <Cell lighter>
        <FormattedMessage id="form.primaryKey" />
        <InformationToolTip>
          <FormattedMessage id="connectionForm.primaryKey.info" />
        </InformationToolTip>
      </Cell>
      <Cell lighter>
        <FormattedMessage id="connector.destination" />
        <InformationToolTip>
          <FormattedMessage id="connectionForm.destinationName.info" />
          <NextLineText>
            <FormattedMessage id="connectionForm.destinationStream.info" />
          </NextLineText>
        </InformationToolTip>
      </Cell>
      <Cell />
    </SchemaHeader>
  );
};

const CatalogSubheader: React.FC = () => (
  <SchemaHeader>
    <CheckboxCell />
    <ArrowCell />
    <ClearSubtitleCell flex={0.4} />
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
);

const SyncCatalogField: React.FC<SchemaViewProps> = ({
  destinationSupportedSyncModes,
  additionalControl,
  field,
  form,
}) => {
  const { value: streams, name: fieldName } = field;

  const [searchString, setSearchString] = useState("");
  const setField = form.setFieldValue;

  const onChangeSchema = useCallback(
    (newValue: SyncSchemaStream[]) => setField(fieldName, newValue),
    [fieldName, setField]
  );

  const onChangeStream = useCallback(
    (newValue: SyncSchemaStream) => onChangeSchema(streams.map((str) => (str.id === newValue.id ? newValue : str))),
    [streams, onChangeSchema]
  );

  const sortedSchema = useMemo(
    () => streams.sort(naturalComparatorBy((syncStream) => syncStream.stream.name)),
    [streams]
  );

  const filteredStreams = useMemo(() => {
    const filters: Array<(s: SyncSchemaStream) => boolean> = [
      (_: SyncSchemaStream) => true,
      searchString
        ? (stream: SyncSchemaStream) => stream.stream.name.toLowerCase().includes(searchString.toLowerCase())
        : null,
    ].filter(Boolean) as Array<(s: SyncSchemaStream) => boolean>;

    return sortedSchema.filter((stream) => filters.every((f) => f(stream)));
  }, [searchString, sortedSchema]);

  return (
    <BatchEditProvider nodes={streams} update={onChangeSchema}>
      <HeaderBlock>
        <FormattedMessage id="form.dataSync" />
        {additionalControl}
      </HeaderBlock>
      <Search onSearch={setSearchString} />
      <StreamsContent>
        <CatalogHeader />
        <CatalogSubheader />
        <BulkHeader destinationSupportedSyncModes={destinationSupportedSyncModes} />
        <TreeViewContainer>
          <CatalogTree
            streams={filteredStreams}
            onChangeStream={onChangeStream}
            destinationSupportedSyncModes={destinationSupportedSyncModes}
          />
        </TreeViewContainer>
      </StreamsContent>
    </BatchEditProvider>
  );
};

export default React.memo(SyncCatalogField);
