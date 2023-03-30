import { faEdit } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import styled from "styled-components";

interface IProps {
  id: string;
  onClick: () => void;
}

const Content = styled.div`
  color: ${({ theme }) => theme.greyColor60};
  font-size: 17px;
  min-width: 17px;
  padding-right: 44px;
  &:hover {
    cursor: pointer;
  }
`;

const Icon = styled(FontAwesomeIcon)`
  color: #4f46e5;
`;
const ConnectorCell: React.FC<IProps> = ({ onClick }) => {
  return (
    <Content onClick={onClick}>
      <Icon icon={faEdit} />
    </Content>
  );
};

export default ConnectorCell;
