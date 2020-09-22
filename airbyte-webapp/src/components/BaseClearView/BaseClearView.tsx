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
  width: 112px;
  height: 112px;
  margin-bottom: 20px;
`;

const BaseClearView: React.FC = props => {
  return (
    <Content>
      <Img src={"/logo.png"} width={112} height={112} alt={"logo"} />
      {props.children}
    </Content>
  );
};

export default BaseClearView;
