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

export const Cell = styled.div<{ flex?: number; light?: boolean }>`
  flex: ${({ flex }) => flex || 1} 0 0;
  padding-right: 10px;
  word-break: break-word;
  color: ${({ theme, light }) => (light ? theme.greyColor40 : "inherit")};
  font-weight: ${({ light }) => (light ? "normal" : "inherit")};

  overflow: hidden;
  text-overflow: ellipsis;
`;

export const LightCell = styled(Cell)`
  color: ${({ theme }) => theme.greyColor60};
  font-weight: normal;
`;
