import styled from "styled-components";

export const Row = styled.div<{
  borderTop?: string;
  borderBottom?: string;
  alignItems?: string;
  height?: string;
}>`
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: ${({ alignItems }) => (alignItems ? alignItems : "center")};
  height: ${({ height }) => (height ? height : "32px")};
  position: relative;

  font-size: 14px;
  line-height: 17px;
  font-weight: normal;
  color: ${({ theme }) => theme.darkPrimaryColor};
  border: none;
  border-top: ${({ borderTop }) => (borderTop ? borderTop : "none")};
  border-bottom: ${({ borderBottom }) => (borderBottom ? borderBottom : "none")};
`;

export const Header = styled(Row)`
  font-weight: 600;
  color: ${({ theme }) => theme.textColor};
  height: 17px;
  padding: 0;
`;

export const Cell = styled.div<{
  flex?: number;
  light?: boolean;
  lighter?: boolean;
  ellipsis?: boolean;
  addWidth?: string;
}>`
  flex: ${({ flex }) => flex || 1} 0 0;
  padding-right: 10px;
  word-break: break-word;
  color: ${({ theme, light, lighter }) => (light ? theme.greyColor40 : lighter ? theme.greyColor60 : "inherit")};
  font-weight: ${({ light, lighter }) => (light || lighter ? "normal" : "inherit")};
  min-width: ${({ addWidth }) => (addWidth ? `${addWidth}px` : "auto")};
  overflow: ${({ ellipsis }) => (ellipsis ? "hidden" : "inherit")};
  text-overflow: ${({ ellipsis }) => (ellipsis ? "ellipsis" : "inherit")};
`;
