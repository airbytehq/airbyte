import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button, H4, Link, Spinner } from "components";
import StatusIcon from "components/StatusIcon";

import { createFormErrorMessage } from "utils/errorStatusMessage";

interface IProps {
  isLoading?: boolean;
  success?: boolean;
  type: "source" | "destination";
  error?: number;
  retry?: () => void;
  linkToSettings?: string;
}

const Content = styled.div`
  min-height: 320px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
`;

const ErrorMessage = styled.div`
  color: ${({ theme }) => theme.dangerColor};
`;

const Title = styled(H4)`
  padding: 16px 0 10px;
`;

const ButtonBox = styled.div`
  min-width: 239px;
  padding-top: 25px;
`;

const LinkButton = styled(Button)`
  color: ${({ theme }) => theme.whiteColor};
  margin-bottom: 6px;
`;

const CheckConnection: React.FC<IProps> = ({ isLoading, type, error, retry, linkToSettings }) => {
  if (error) {
    const errorMessage = createFormErrorMessage({ status: error });

    return (
      <Content>
        <StatusIcon big />
        <Title>
          <FormattedMessage id="connection.testsFailed" />
        </Title>
        <ErrorMessage>{errorMessage}</ErrorMessage>
        <ButtonBox>
          <LinkButton full as={Link} to={linkToSettings}>
            <FormattedMessage id={`connection.${type}CheckSettings`} />
          </LinkButton>
          <Button secondary full onClick={retry}>
            <FormattedMessage id={`connection.${type}TestAgain`} />
          </Button>
        </ButtonBox>
      </Content>
    );
  }

  if (isLoading) {
    return (
      <Content>
        <Spinner />
        <Title>
          <FormattedMessage id={`tables.${type}IsValidating`} />
        </Title>
        <FormattedMessage id={`tables.${type}IsValidatingBefore`} />
      </Content>
    );
  }

  return (
    <Content>
      <StatusIcon status="success" big />
      <Title>
        <FormattedMessage id="connection.testsPassed" />
      </Title>
    </Content>
  );
};

export default CheckConnection;
