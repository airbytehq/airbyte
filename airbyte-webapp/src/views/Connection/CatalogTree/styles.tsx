import styled from "styled-components";

import { Cell } from "components";

export const HeaderCell = styled(Cell)`
  font-size: 10px;
  line-height: 13px;
`;

export const CheckboxCell = styled(HeaderCell)`
  max-width: 43px;
  text-align: center;
  margin-left: -43px;
`;

export const ArrowCell = styled(HeaderCell)`
  max-width: 40px;
  width: 40px;
`;

export const NameContainer = styled.span`
  padding-left: 30px;
`;
