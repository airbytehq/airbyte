import React from "react";
import styled from "styled-components";
import { Row } from "components/SimpleTableComponents";

const RowWrapper = styled.div<{ depth?: number }>`
  height: 40px;
  border-bottom: 1px solid ${({ theme }) => theme.greyColor20};
  margin-left: ${({ depth = 0 }) => depth * 64}px;
`;

const RowContent = styled(Row)`
  height: 100%;
  white-space: nowrap;
`;

const TreeRowWrapper: React.FC<{ depth?: number }> = ({ depth, children }) => (
  <RowWrapper depth={depth}>
    <RowContent>{children}</RowContent>
  </RowWrapper>
);

export { TreeRowWrapper };
