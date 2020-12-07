import styled from "styled-components";

const TreeItem = styled.div<{ isChild?: boolean }>`
  height: 40px;
  border-bottom: 1px solid ${({ theme }) => theme.greyColor20};
  margin-left: ${({ isChild }) => (isChild ? 64 : 0)}px;
`;

export default TreeItem;
