import React from "react";
import { H1 } from "components/base";
import styled from "styled-components";

type TitlesBlockProps = {
  title: React.ReactNode;
  children?: React.ReactNode;
};

const TitlesContent = styled.div`
  padding: 42px 0 33px;
  color: ${({ theme }) => theme.textColor};
  max-width: 493px;
`;

const Text = styled.div`
  padding-top: 10px;
  font-weight: normal;
  font-size: 13px;
  line-height: 20px;
  text-align: center;
`;

const TitlesBlock: React.FC<TitlesBlockProps> = ({ title, children }) => {
  return (
    <TitlesContent>
      <H1 center bold>
        {title}
      </H1>
      <Text>{children}</Text>
    </TitlesContent>
  );
};

export default TitlesBlock;
