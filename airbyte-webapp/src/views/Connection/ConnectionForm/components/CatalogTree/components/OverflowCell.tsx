import styled from "styled-components";
import { Cell } from "components/SimpleTableComponents";

const OverflowCell = styled(Cell)`
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: default;
`;

export { OverflowCell };
