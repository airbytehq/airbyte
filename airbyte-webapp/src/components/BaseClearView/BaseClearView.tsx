import React from "react";
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

  &.clickable:hover {
    cursor: pointer;
  }
`;

const MainInfo = styled.div`
  display: flex;
  align-items: center;
  flex-direction: column;
`;

interface BaseClearViewProps {
  onLogoClick?: React.MouseEventHandler;
}

const BaseClearView: React.FC<BaseClearViewProps> = ({ children, onLogoClick }) => {
  return (
    <Content>
      <MainInfo>
        <LogoImg
          src="/logo.png"
          alt="Airbyte logo"
          onClick={onLogoClick}
          className={onLogoClick ? "clickable" : undefined}
        />
        {children}
      </MainInfo>
      <Version />
    </Content>
  );
};

export default BaseClearView;
