import React from "react";
import { useIntl } from "react-intl";
import { Link } from "react-router-dom";
import styled from "styled-components";

import Version from "components/Version";

const Content = styled.div`
  height: 100%;
  width: 100%;
  padding: 34px 0 13px;
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: space-between;
`;

const LogoImg = styled.img`
  width: 90px;
  height: 94px;
  margin-bottom: 20px;
`;

const MainInfo = styled.div`
  min-width: 550px;
  display: flex;
  align-items: center;
  flex-direction: column;
`;

const BaseClearView: React.FC = ({ children }) => {
  const { formatMessage } = useIntl();
  return (
    <Content>
      <MainInfo>
        <Link to="..">
          <LogoImg src="/logo.png" alt={formatMessage({ id: "ui.goBack" })} />
        </Link>
        {children}
      </MainInfo>
      <Version />
    </Content>
  );
};

export default BaseClearView;
