import React from "react";
import styled from "styled-components";

interface TitlesBlockProps {
  title: React.ReactNode;
  children?: React.ReactNode;
  testId?: string;
}

const TitlesContent = styled.div`
  padding: 42px 0 33px;
  color: ${({ theme }) => theme.whiteColor};
  max-width: 493px;
`;

const Title = styled.h1`
  font-size: ${({ theme }) => theme.h1?.fontSize || "28px"};
  line-height: ${({ theme }) => theme.h1?.lineHeight || "34px"};
  font-style: normal;
  font-weight: bold;
  display: block;
  text-align: center;
`;

const Text = styled.div`
  padding-top: 10px;
  font-weight: normal;
  font-size: 16px;
  line-height: 20px;
  text-align: center;
  color: #8f9ac2;
`;

const TitlesBlock: React.FC<TitlesBlockProps> = ({ title, children }) => {
  return (
    <TitlesContent>
      <Title>{title}</Title>
      <Text>{children}</Text>
    </TitlesContent>
  );
};

export default TitlesBlock;
