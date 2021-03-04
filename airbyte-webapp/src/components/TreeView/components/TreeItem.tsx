import styled from "styled-components";

const TreeItem = styled.div<{ depth?: number }>`
  height: 40px;
  border-bottom: 1px solid ${({ theme }) => theme.greyColor20};
  margin-left: ${({ depth = 0 }) => depth * 64}px;
`;

export default TreeItem;
