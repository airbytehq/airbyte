import dayjs from "dayjs";
import { useIntl } from "react-intl";
import styled from "styled-components";

import { AttemptRead } from "core/request/AirbyteClient";

import { getFailureFromAttempt, isCancelledAttempt } from "../utils";

interface IProps {
  attempts?: AttemptRead[];
}

const ExpandedFailureContainer = styled.div`
  font-size: 12px;
  line-height: 15px;
  padding: 10px;
  padding-left: 40px;
  color: ${({ theme }) => theme.greyColor40};
`;

const FailureDateDisplay = styled.span`
  font-style: italic;
`;

const ErrorDetails: React.FC<IProps> = ({ attempts }) => {
  const { formatMessage } = useIntl();

  if (!attempts?.length) {
    return null;
  }

  const getInternalFailureMessage = (attempt: AttemptRead) => {
    const failure = getFailureFromAttempt(attempt);
    const failureMessage = failure?.internalMessage ?? formatMessage({ id: "errorView.unknown" });

    return `${formatMessage({
      id: "sources.additionalFailureInfo",
    })}: ${failureMessage}`;
  };

  const attempt = attempts[attempts.length - 1];
  const failure = getFailureFromAttempt(attempt);
  const isCancelled = isCancelledAttempt(attempt);

  if (!failure || isCancelled) {
    return null;
  }

  const internalMessage = getInternalFailureMessage(attempt);
  return (
    <ExpandedFailureContainer>
      {!!failure.timestamp && (
        <FailureDateDisplay>{dayjs.utc(failure.timestamp).format("YYYY-MM-DD HH:mm:ss")} - </FailureDateDisplay>
      )}
      {internalMessage}
    </ExpandedFailureContainer>
  );
};

export default ErrorDetails;
