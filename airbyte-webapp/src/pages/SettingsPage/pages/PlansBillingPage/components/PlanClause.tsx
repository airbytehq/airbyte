import React from "react";
import styled from "styled-components";

import { TickIcon } from "components/icons/TickIcon";

interface IProps {
  text?: string;
}

const Container = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const Text = styled.div`
  font-weight: 400;
  font-size: 14px;
  color: ${({ theme }) => theme.black300};
  margin-left: 16px;
`;

const PlanClause: React.FC<IProps> = ({ text }) => {
  return (
    <Container>
      <TickIcon />
      <Text>{text}</Text>
    </Container>
  );
};

export default PlanClause;
