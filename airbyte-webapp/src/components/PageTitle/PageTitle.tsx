import React from "react";
import styled from "styled-components";

import { H3 } from "components";

interface PageTitleProps {
  withLine?: boolean;
  middleComponent?: React.ReactNode;
  middleTitleBlock?: React.ReactNode;
  endComponent?: React.ReactNode;
  title?: React.ReactNode;
  subText?: React.ReactNode;
  withPadding?: boolean;
}

export const MainContainer = styled.div<{ withLine?: boolean; withPadding?: boolean }>`
  padding: ${({ withPadding }) => (withPadding ? `24px 38px` : "0")};
  // padding-top: 35px;
  border-bottom: ${({ withLine }) => (withLine ? `1px solid #D1D5DB` : "none")};
  position: relative;
  z-index: 2;
  color: ${({ theme }) => theme.darkPrimaryColor};
  // display: flex;
  // flex-direction: row;
  // justify-content: space-between;
  // align-items: center;
  //flex-direction: column;
`;

export const MiddleBlock = styled.div`
  flex: 1 0 0;
  display: flex;
  justify-content: center;
`;

export const MiddleTitleBlock = styled(H3)`
  flex: 1 0 0;
  display: flex;
  justify-content: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
  font-weight: 500;
  font-size: 20px;
  line-height: 32px;
  color: #000;
`;

export const RemarkBlock = styled.div`
  font-size: 14px;
  line-height: 30px;
  color: #6b6b6f;
  margin-top: 10px;
`;

const PageTitle: React.FC<PageTitleProps> = ({
  title,
  subText,
  withLine,
  middleComponent,
  middleTitleBlock,
  endComponent,
  withPadding,
}) => (
  <MainContainer withLine={withLine} withPadding={withPadding}>
    <TitleBlock>{title}</TitleBlock>
    {subText && <RemarkBlock>{subText}</RemarkBlock>}
    {middleTitleBlock ? (
      <MiddleTitleBlock>{middleTitleBlock}</MiddleTitleBlock>
    ) : (
      <MiddleBlock>{middleComponent}</MiddleBlock>
    )}
    <EndBlock>{endComponent}</EndBlock>
  </MainContainer>
);

export default PageTitle;
