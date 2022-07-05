import React from "react";
import styled from "styled-components";

interface IProps {
  text: React.ReactNode;
  description?: React.ReactNode;
}

const Content = styled.div`
  padding: 74px 0 111px;
  text-align: center;
  font-size: 20px;
  line-height: 27px;
  color: ${({ theme }) => theme.textColor};
`;

const ImgBlock = styled.div`
  height: 80px;
  width: 80px;
  border-radius: 50%;
  background: ${({ theme }) => theme.greyColor20};
  margin: 0 auto 10px;
  text-align: center;
  padding: 20px 0;
`;

const Description = styled.div`
  font-weight: normal;
  font-size: 14px;
  line-height: 19px;
  color: ${({ theme }) => theme.greyColor60};
  margin-top: 5px;
`;

const EmptyResourceBlock: React.FC<IProps> = ({ text, description }) => (
  <Content>
    <ImgBlock>
      <img src="/cactus.png" height={40} alt="cactus" />
    </ImgBlock>
    {text}
    <Description>{description}</Description>
  </Content>
);

export default EmptyResourceBlock;
