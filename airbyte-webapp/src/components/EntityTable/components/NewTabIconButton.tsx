import React from "react";
import { FormattedMessage } from "react-intl";
import { Link } from "react-router-dom";
import styled from "styled-components";

import { Tooltip } from "components/base/Tooltip";
import { NewTabIcon } from "components/icons/NewTabIcon";

import { RoutePaths } from "pages/routePaths";

interface Props {
  id: string;
  type: "Connections" | "Source" | "Destination";
}

const Content = styled(Link)`
  color: #aaa;
  margin-left: 6px;
  &:hover {
    color: ${({ theme }) => theme.primaryColor};
    cursor: pointer;
    font-weight: 500;
  }
`;

const NewTabIconButton: React.FC<Props> = ({ id, type }) => {
  return (
    <Content to={`/${RoutePaths[type]}/${id}`} target="_blank">
      <Tooltip control={<NewTabIcon width={12} height={12} />} placement="top">
        <FormattedMessage id="table.name.open.newTab" />
      </Tooltip>
    </Content>
  );
};

export default NewTabIconButton;
