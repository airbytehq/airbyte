import styled from "styled-components";
import React from "react";

type IProps = {
  img?: string;
  className?: string;
};

export const Content = styled.div`
  height: 25px;
  width: 25px;
  background: ${({ theme }) => theme.brightColor};
  box-shadow: 0 1px 2px 0 ${({ theme }) => theme.shadowColor};
  border-radius: 50%;
  text-align: center;
  padding: 4px 0 3px;
`;

export const Image = styled.img`
  border-radius: 50%;
`;

const ImageBlock: React.FC<IProps> = ({ img, className }) => (
  <Content className={className}>
    <Image src={img || "/default-logo-catalog.svg"} height={18} alt={"logo"} />
  </Content>
);

export default ImageBlock;
