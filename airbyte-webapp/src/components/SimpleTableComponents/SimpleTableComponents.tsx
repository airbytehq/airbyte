import styled from "styled-components";

export const Row = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  height: 32px;
  position: relative;

  font-size: 14px;
  line-height: 17px;
  font-weight: normal;
  color: ${({ theme }) => theme.darkPrimaryColor};
  border: none;
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
  flush?: boolean;
}>`
  flex: ${({ flex }) => flex || 1} 0 0;
  padding-right: ${({ flush }) => (flush ? 0 : 10)}px;
  min-width: 0;

  word-break: break-word;
  color: ${({ theme, light, lighter }) => (light ? theme.greyColor40 : lighter ? theme.greyColor60 : "inherit")};
  font-weight: ${({ light, lighter }) => (light || lighter ? "normal" : "inherit")};

  overflow: ${({ ellipsis }) => (ellipsis ? "hidden" : "inherit")};
  text-overflow: ${({ ellipsis }) => (ellipsis ? "ellipsis" : "inherit")};
`;
