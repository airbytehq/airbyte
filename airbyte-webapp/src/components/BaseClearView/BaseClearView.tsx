import React from "react";
import styled from "styled-components";

const Content = styled.div`
  height: 100%;
  width: 100%;
  padding-top: 34px;
  display: flex;
  align-items: center;
  flex-direction: column;
`;

const Img = styled.img`
  width: 90px;
  height: 94px;
  margin-bottom: 20px;
`;

const BaseClearView: React.FC = props => {
  return (
    <Content>
      <Img src={"/logo.png"} alt={"logo"} />
      {props.children}
    </Content>
  );
};

export default BaseClearView;
