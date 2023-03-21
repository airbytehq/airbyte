import styled from "styled-components";

import { Row, Cell } from "components";

export const FirstCellFlexValue = 7;

export const HeaderText = styled.div`
  color: #27272a;
  font-style: normal;
  font-weight: 400;
  font-size: 14px;
`;

export const FirstHeaderText = styled(HeaderText)`
  font-weight: 700;
  font-size: 24px;
`;

export const BodyRow = styled(Row)`
  padding: 20px 0;
`;

export const FirstCell = styled(Cell)`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
`;

export const BodyCell = styled(Cell)`
  width: 100%;
  display: flex;
  justify-content: center;
`;
