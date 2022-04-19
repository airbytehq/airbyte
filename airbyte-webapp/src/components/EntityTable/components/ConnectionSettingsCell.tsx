import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCog } from "@fortawesome/free-solid-svg-icons";

import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routes";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";

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

  tr:hover & {
    display: block;
  }
  &:hover {
    color: ${({ theme }) => theme.greyColor70};
  }
`;

const ConnectorCell: React.FC<IProps> = ({ id }) => {
  const { push } = useRouter();
  const { workspaceId } = useCurrentWorkspace();

  const openSettings = (event: React.MouseEvent) => {
    event.stopPropagation();
    // TODO: Replace with link instead of push
    push(
      `/${workspaceId}/${RoutePaths.Connections}/${id}/${RoutePaths.Settings}`
    );
  };

  return (
    <Content onClick={openSettings}>
      <Icon icon={faCog} />
    </Content>
  );
};

export default ConnectorCell;
