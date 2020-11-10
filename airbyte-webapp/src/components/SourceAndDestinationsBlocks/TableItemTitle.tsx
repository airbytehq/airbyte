import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { H5 } from "../Titles";
import Button from "../Button";

type IProps = {
  type: "source" | "destination";
};

const Content = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px 18px 27px;
`;

const TableItemTitle: React.FC<IProps> = ({ type }) => {
  return (
    <Content>
      <H5>
        <FormattedMessage id={`tables.${type}s`} />
      </H5>
      <Button>
        <FormattedMessage id={`tables.${type}Add`} />
      </Button>
    </Content>
  );
};

export default TableItemTitle;
