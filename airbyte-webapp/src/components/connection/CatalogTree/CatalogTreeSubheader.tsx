import classnames from "classnames";
import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Cell, Header } from "components/SimpleTableComponents";

import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";

import styles from "./CatalogTreeSubheader.module.scss";

const SubtitleCell = styled(Cell).attrs(() => ({ light: true }))`
  font-size: 10px;
  line-height: 12px;
  border-top: 1px solid ${({ theme }) => theme.greyColor0};
  padding-top: 5px;
`;

const ClearSubtitleCell = styled(SubtitleCell)`
  border-top: none;
`;

export const CatalogTreeSubheader: React.FC = () => {
  const { mode } = useConnectionFormService();

  const catalogSubheaderStyle = classnames({
    [styles.catalogSubheader]: mode !== "readonly",
    [styles.readonlyCatalogSubheader]: mode === "readonly",
  });

  return (
    <Header className={catalogSubheaderStyle}>
      <Cell flex={0.8} />
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
