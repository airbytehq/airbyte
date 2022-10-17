import classnames from "classnames";
import React, { useCallback, useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Cell, Header } from "components/SimpleTableComponents";
import { CheckBox } from "components/ui/CheckBox";
import { LoadingBackdrop } from "components/ui/LoadingBackdrop";
import { InfoTooltip, TooltipLearnMoreLink } from "components/ui/Tooltip";

import { SyncSchemaStream } from "core/domain/catalog";
import { BatchEditProvider, useBulkEdit } from "hooks/services/BulkEdit/BulkEditService";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { links } from "utils/links";
import { naturalComparatorBy } from "utils/objects";

import styles from "./CatalogTree.module.scss";
import { CatalogTreeRows } from "./CatalogTreeRows";
import { CatalogTreeSearch } from "./CatalogTreeSearch";
import { BulkHeader } from "./components/BulkHeader";

const SubtitleCell = styled(Cell).attrs(() => ({ lighter: true }))`
  font-size: 10px;
  line-height: 12px;
  border-top: 1px solid ${({ theme }) => theme.greyColor0};
  padding-top: 5px;
`;

const ClearSubtitleCell = styled(SubtitleCell)`
  border-top: none;
`;

const NextLineText = styled.div`
  margin-top: 10px;
`;

interface CatalogTreeProps {
  streams: SyncSchemaStream[];
  onStreamsChanged: (streams: SyncSchemaStream[]) => void;
  isLoading: boolean;
}

const CatalogHeader: React.FC = () => {
  const { mode } = useConnectionFormService();
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
          <TooltipLearnMoreLink url={links.syncModeLink} />
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

const CatalogSubheader: React.FC = () => {
  const { mode } = useConnectionFormService();

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

const CatalogTreeComponent: React.FC<React.PropsWithChildren<CatalogTreeProps>> = ({
  streams,
  onStreamsChanged,
  isLoading,
}) => {
  const { mode } = useConnectionFormService();

  const [searchString, setSearchString] = useState("");

  const onSingleStreamChanged = useCallback(
    (newValue: SyncSchemaStream) => onStreamsChanged(streams.map((str) => (str.id === newValue.id ? newValue : str))),
    [streams, onStreamsChanged]
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
    <BatchEditProvider nodes={streams} update={onStreamsChanged}>
      <LoadingBackdrop loading={isLoading}>
        {mode !== "readonly" && <CatalogTreeSearch onSearch={setSearchString} />}
        <CatalogHeader />
        <CatalogSubheader />
        <BulkHeader />
        <div className={styles.catalogTreeContainer}>
          <CatalogTreeRows streams={filteredStreams} onStreamChanged={onSingleStreamChanged} />
        </div>
      </LoadingBackdrop>
    </BatchEditProvider>
  );
};

export const CatalogTree = React.memo(CatalogTreeComponent);
