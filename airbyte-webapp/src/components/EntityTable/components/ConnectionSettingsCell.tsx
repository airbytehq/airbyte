import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCog } from "@fortawesome/free-solid-svg-icons";
import useRouter from "hooks/useRouter";
import { Routes } from "../../../pages/routes";

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

  const openSettings = (event: React.MouseEvent) => {
    event.stopPropagation();
    push(`${Routes.Connections}/${id}${Routes.Settings}`);
  };

  return (
    <Content onClick={openSettings}>
      <Icon icon={faCog} />
    </Content>
  );
};

export default ConnectorCell;
