import styled from "styled-components";
import React from "react";

type IProps = {
  img: string;
};

export const Content = styled.div`
  height: 25px;
  width: 25px;
  background: ${({ theme }) => theme.brightColor};
  box-shadow: 0 1px 2px 0 ${({ theme }) => theme.shadowColor};
  border-radius: 50%;
  text-align: center;
  padding: 3px 0;
`;

const ImageBlock: React.FC<IProps> = ({ img }) => (
  <Content>
    <img src={img} height={18} alt={"logo"} />
  </Content>
);

export default ImageBlock;
