import React from "react";
import styled from "styled-components";

import { H5 } from "components";
import ContentCard from "components/ContentCard";

interface IProps {
  title: React.ReactElement;
  actions: React.ReactElement;
}

const TitleBlockComponent = styled(ContentCard)`
  margin-bottom: 12px;
  padding: 19px 20px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Text = styled.div`
  margin-left: 20px;
  font-size: 11px;
  line-height: 13px;
  color: ${({ theme }) => theme.greyColor40};
  white-space: pre-line;
`;

const TitleBlock: React.FC<IProps> = ({ title, actions }) => {
  return (
    <TitleBlockComponent>
      <Text>
        <H5 bold>{title}</H5>
      </Text>
      <div>{actions}</div>
    </TitleBlockComponent>
  );
};

export default TitleBlock;
