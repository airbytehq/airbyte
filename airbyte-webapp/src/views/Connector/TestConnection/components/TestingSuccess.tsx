import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

const Text = styled.div`
  font-size: 28px;
  line-height: 48px;
  margin-bottom: 120px;
`;

const Image = styled.img`
  width: 100px;
  height: 100px;
`;

const TestingSuccess: React.FC<{
  type: "destination" | "source" | "connection";
}> = ({ type }) => {
  return (
    <>
      <Text>
        <FormattedMessage id={`form.${type}.validated`} />
      </Text>
      <Image src="/icons/finish-icon.png" alt="finish-icon" />
    </>
  );
};

export default TestingSuccess;
