import React from "react";

import styled from "styled-components";
import { H3 } from "../Titles";

type IProps = {
  withLine?: boolean;
  title: string | React.ReactNode;
};

export const MainContainer = styled.div<{ withLine?: boolean }>`
  padding: 20px 25px 18px;
  border-bottom: ${({ theme, withLine }) =>
    withLine ? `1px solid ${theme.greyColor20}` : "none"};
  margin-bottom: ${({ withLine }) => (withLine ? "17px" : 0)};
  position: relative;
  z-index: 2;
  color: ${({ theme }) => theme.darkPrimaryColor};
`;

const PageTitle: React.FC<IProps> = ({ title, withLine }) => (
  <MainContainer withLine={withLine}>
    <H3>{title}</H3>
  </MainContainer>
);

export default PageTitle;
