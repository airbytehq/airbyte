import styled from "styled-components";
import { Row } from "../../SimpleTableComponents";

const ItemRow = styled(Row)<{ isChild?: boolean }>`
  height: 100%;
  white-space: nowrap;
`;

export default ItemRow;
