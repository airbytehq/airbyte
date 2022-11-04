import { faEdit } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import styled from "styled-components";

import { Link } from "components";

// import { useCurrentWorkspace } from "hooks/services/useWorkspace";
// import { ConnectionSettingsRoutes } from "pages/ConnectionPage/pages/ConnectionItemPage/ConnectionSettingsRoutes";
//
// import { RoutePaths } from "../../../pages/routePaths";

interface IProps {
  id: string;
}

const Content = styled.div`
  color: ${({ theme }) => theme.greyColor60};
  font-size: 17px;
  min-width: 17px;
  padding-right: 44px;
`;

const Icon = styled(FontAwesomeIcon)`
  //display: none;
  color: #4f46e5;

  // tr:hover & {
  //   display: block;
  // }
  // &:hover {
  //   color: ${({ theme }) => theme.greyColor70};
  // }
`;
// { id }
const ConnectorCell: React.FC<IProps> = () => {
  // const { workspaceId } = useCurrentWorkspace();

  // const openSettings = (event: React.MouseEvent) => {
  //   event.stopPropagation();
  // };

  // const settingPath = `/${RoutePaths.Workspaces}/${workspaceId}/${RoutePaths.Connections}/${id}/${ConnectionSettingsRoutes.REPLICATION}`;
  //  to={settingPath} onClick={openSettings}
  return (
    <Content>
      <Link to="">
        <Icon icon={faEdit} />
      </Link>
    </Content>
  );
};

export default ConnectorCell;
