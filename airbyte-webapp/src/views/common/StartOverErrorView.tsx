import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";

import useRouter from "hooks/useRouter";
import { ErrorOccurredView } from "views/common/ErrorOccurredView";

const ResetSection = styled.div`
  margin-top: 30px;
  display: flex;
  justify-content: space-around;
`;

export const StartOverErrorView: React.FC<{
  message?: string;
  onReset?: () => void;
}> = ({ message, onReset }) => {
  const { push } = useRouter();
  return (
    <ErrorOccurredView message={message ?? <FormattedMessage id="errorView.notFound" />}>
      <ResetSection>
        <Button
          onClick={() => {
            push("..");
            onReset?.();
          }}
        >
          <FormattedMessage id="errorView.startOver" />
        </Button>
      </ResetSection>
    </ErrorOccurredView>
  );
};
