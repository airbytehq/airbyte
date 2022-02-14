import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCog } from "@fortawesome/free-solid-svg-icons";

import { RoutePaths } from "pages/routes";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { Link } from "components";

type IProps = {
  id: string;
};

const Content = styled.div`
  color: ${({ theme }) => theme.greyColor60};
  font-size: 17px;
  min-width: 17px;
`;

const Icon = styled(FontAwesomeIcon)`
  display: none;
  color: ${({ theme }) => theme.greyColor60};

  tr:hover & {
    display: block;
  }
  &:hover {
    color: ${({ theme }) => theme.greyColor70};
  }
`;

const ConnectorCell: React.FC<IProps> = ({ id }) => {
  const { workspaceId } = useCurrentWorkspace();

  const openSettings = (event: React.MouseEvent) => {
    event.stopPropagation();
  };

  const settingPath = `/${RoutePaths.Workspaces}/${workspaceId}/${RoutePaths.Connections}/${id}/${RoutePaths.Settings}`;
  return (
    <Content onClick={openSettings}>
      <Link to={settingPath}>
        <Icon icon={faCog} />
      </Link>
    </Content>
  );
};

export default ConnectorCell;
