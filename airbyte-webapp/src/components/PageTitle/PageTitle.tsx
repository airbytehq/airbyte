import React from "react";
import styled from "styled-components";

import { H3 } from "components";

type IProps = {
  withLine?: boolean;
  middleComponent?: React.ReactNode;
  endComponent?: React.ReactNode;
  title: React.ReactNode;
};

export const MainContainer = styled.div<{ withLine?: boolean }>`
  padding: 20px 32px 18px;
  border-bottom: ${({ theme, withLine }) => (withLine ? `1px solid ${theme.greyColor20}` : "none")};
  position: relative;
  z-index: 2;
  color: ${({ theme }) => theme.darkPrimaryColor};

  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
`;

export const MiddleBlock = styled.div`
  flex: 1 0 0;
  display: flex;
  justify-content: center;
`;

export const EndBlock = styled.div`
  flex: 1 0 0;
  display: flex;
  justify-content: flex-end;
`;

export const TitleBlock = styled(H3)`
  flex: 1 0 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const PageTitle: React.FC<IProps> = ({ title, withLine, middleComponent, endComponent }) => (
  <MainContainer withLine={withLine}>
    <TitleBlock>{title}</TitleBlock>
    <MiddleBlock>{middleComponent}</MiddleBlock>
    <EndBlock>{endComponent}</EndBlock>
  </MainContainer>
);

export default PageTitle;
