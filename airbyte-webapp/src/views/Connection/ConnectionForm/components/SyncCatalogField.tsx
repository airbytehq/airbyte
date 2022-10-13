import classnames from "classnames";
import { FieldProps } from "formik";
import React, { useCallback, useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { CheckBox, H5 } from "components";
import { InfoTooltip, TooltipLearnMoreLink } from "components/base/Tooltip";
import { LoadingBackdrop } from "components/LoadingBackdrop";
import { Cell, Header } from "components/SimpleTableComponents";

import { useConfig } from "config";
import { SyncSchemaStream } from "core/domain/catalog";
import { DestinationSyncMode } from "core/request/AirbyteClient";
import { BatchEditProvider, useBulkEdit } from "hooks/services/BulkEdit/BulkEditService";
import { naturalComparatorBy } from "utils/objects";
import CatalogTree from "views/Connection/CatalogTree";

import { BulkHeader } from "../../CatalogTree/components/BulkHeader";
import { ConnectionFormMode } from "../ConnectionForm";
import Search from "./Search";
import styles from "./SyncCatalogField.module.scss";

const TreeViewContainer = styled.div<{ mode?: ConnectionFormMode }>`
  margin-bottom: 29px;
  max-height: 600px;
  overflow-y: auto;
  --webkit-overlay: true;

  width: 100%;
`;

const SubtitleCell = styled(Cell).attrs(() => ({ lighter: true }))`
  font-size: 10px;
  line-height: 12px;
  border-top: 1px solid ${({ theme }) => theme.greyColor0};
  padding-top: 5px;
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

interface SchemaViewProps extends FieldProps<SyncSchemaStream[]> {
  additionalControl?: React.ReactNode;
  destinationSupportedSyncModes: DestinationSyncMode[];
  isSubmitting: boolean;
  mode?: ConnectionFormMode;
}

const CatalogHeader: React.FC<{ mode?: ConnectionFormMode }> = ({ mode }) => {
  const config = useConfig();
  const { onCheckAll, selectedBatchNodeIds, allChecked } = useBulkEdit();
  const catalogHeaderStyle = classnames({
    [styles.catalogHeader]: mode !== "readonly",
    [styles.readonlyCatalogHeader]: mode === "readonly",
  });

  return (
    <Header className={catalogHeaderStyle}>
      {mode !== "readonly" && (
        <Cell className={styles.checkboxCell}>
          <CheckBox
            onChange={onCheckAll}
            indeterminate={selectedBatchNodeIds.length > 0 && !allChecked}
            checked={allChecked}
          />
        </Cell>
      )}
      {mode !== "readonly" && <Cell flex={0.2} />}
      <Cell lighter flex={0.4}>
        <FormattedMessage id="sources.sync" />
      </Cell>
      <Cell lighter>
        <FormattedMessage id="sources.source" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.source.info" />
        </InfoTooltip>
      </Cell>
      <Cell />
      <Cell lighter flex={1.5}>
        <FormattedMessage id="form.syncMode" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.syncType.info" />
          <TooltipLearnMoreLink url={config.links.syncModeLink} />
        </InfoTooltip>
      </Cell>
      <Cell lighter>
        <FormattedMessage id="form.cursorField" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.cursor.info" />
        </InfoTooltip>
      </Cell>
      <Cell lighter>
        <FormattedMessage id="form.primaryKey" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.primaryKey.info" />
        </InfoTooltip>
      </Cell>
      <Cell lighter>
        <FormattedMessage id="connector.destination" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.destinationName.info" />
          <NextLineText>
            <FormattedMessage id="connectionForm.destinationStream.info" />
          </NextLineText>
        </InfoTooltip>
      </Cell>
      <Cell />
    </Header>
  );
};

const CatalogSubheader: React.FC<{ mode?: ConnectionFormMode }> = ({ mode }) => {
  const catalogSubheaderStyle = classnames({
    [styles.catalogSubheader]: mode !== "readonly",
    [styles.readonlyCatalogSubheader]: mode === "readonly",
  });

  return (
    <Header className={catalogSubheaderStyle}>
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
    </Header>
  );
};

const SyncCatalogField: React.FC<SchemaViewProps> = ({
  destinationSupportedSyncModes,
  additionalControl,
  field,
  form,
  isSubmitting,
  mode,
}) => {
  const { value: streams, name: fieldName } = field;

  const [searchString, setSearchString] = useState("");
  const setField = form.setFieldValue;

  const onChangeSchema = useCallback(
    (newValue: SyncSchemaStream[]) => {
      setField(fieldName, newValue);
    },
    [fieldName, setField]
  );

  const onChangeStream = useCallback(
    (newValue: SyncSchemaStream) => onChangeSchema(streams.map((str) => (str.id === newValue.id ? newValue : str))),
    [streams, onChangeSchema]
  );

  const sortedSchema = useMemo(
    () => streams.sort(naturalComparatorBy((syncStream) => syncStream.stream?.name ?? "")),
    [streams]
  );

  const filteredStreams = useMemo(() => {
    const filters: Array<(s: SyncSchemaStream) => boolean> = [
      (_: SyncSchemaStream) => true,
      searchString
        ? (stream: SyncSchemaStream) => stream.stream?.name.toLowerCase().includes(searchString.toLowerCase())
        : null,
    ].filter(Boolean) as Array<(s: SyncSchemaStream) => boolean>;

    return sortedSchema.filter((stream) => filters.every((f) => f(stream)));
  }, [searchString, sortedSchema]);

  return (
    <BatchEditProvider nodes={streams} update={onChangeSchema}>
      <LoadingBackdrop loading={isSubmitting}>
        <HeaderBlock>
          {mode !== "readonly" ? (
            <>
              <H5 bold>
                <FormattedMessage id="form.dataSync" />
              </H5>
              {additionalControl}
            </>
          ) : (
            <H5 bold>
              <FormattedMessage id="form.dataSync.readonly" />
            </H5>
          )}
        </HeaderBlock>
        {mode !== "readonly" && <Search onSearch={setSearchString} />}
        <CatalogHeader mode={mode} />
        <CatalogSubheader mode={mode} />
        <BulkHeader destinationSupportedSyncModes={destinationSupportedSyncModes} />
        <TreeViewContainer mode={mode}>
          <CatalogTree
            streams={filteredStreams}
            onChangeStream={onChangeStream}
            destinationSupportedSyncModes={destinationSupportedSyncModes}
            mode={mode}
          />
        </TreeViewContainer>
      </LoadingBackdrop>
    </BatchEditProvider>
  );
};

export default React.memo(SyncCatalogField);
