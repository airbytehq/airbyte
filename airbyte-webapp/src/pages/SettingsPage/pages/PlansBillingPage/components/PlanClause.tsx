import React from "react";
import styled from "styled-components";

import { TickIcon } from "components/icons/TickIcon";

import { PlanItem } from "core/domain/payment";

interface IProps {
  planItem: PlanItem;
  clause: string | React.ReactElement;
}

const Container = styled.div`
  width: 50%;
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-bottom: 20px;
`;

const Text = styled.div`
  font-weight: 400;
  font-size: 14px;
  color: ${({ theme }) => theme.black300};
  margin-left: 16px;
`;

export const PlanClause: React.FC<IProps> = React.memo(({ planItem, clause }) => {
  if (clause === "") {
    return null;
  }
  return (
    <Container key={planItem.planItemid}>
      <TickIcon />
      <Text key={planItem.planItemid}>{clause}</Text>
    </Container>
  );
});
