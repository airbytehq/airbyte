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

const Img = styled.img`
  width: 90px;
  height: 94px;
  margin-bottom: 20px;
`;

const MainInfo = styled.div`
  display: flex;
  align-items: center;
  flex-direction: column;
`;

const BaseClearView: React.FC = (props) => {
  return (
    <Content>
      <MainInfo>
        <Img src="/logo.png" alt="logo" />
        {props.children}
      </MainInfo>
      <Version />
    </Content>
  );
};

export default BaseClearView;
