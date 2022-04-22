import { faEnvelope } from "@fortawesome/free-regular-svg-icons";
import { AuthErrorCodes } from "firebase/auth";
import { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import { InfoBox } from "components/InfoBox";

import { useNotificationService } from "hooks/services/Notification";
import { useAuthService } from "packages/cloud/services/auth/AuthService";

interface Props {
  className?: string;
}

const ResendEmailLink = styled.button`
  appearance: none;
  background: none;
  padding: none;
  border: none;
  font-size: inherit;
  text-decoration: underline;
  cursor: pointer;
  padding: 0;
  margin: 0;
  display: inline;
  color: ${({ theme }) => theme.mediumPrimaryColor};
`;

enum FirebaseAuthMessageId {
  NetworkFailure = "firebase.auth.error.networkRequestFailed",
  TooManyRequests = "firebase.auth.error.tooManyRequests",
  DefaultError = "firebase.auth.error.default",
}

export const EmailVerificationHint: React.FC<Props> = ({ className }) => {
  const { sendEmailVerification } = useAuthService();
  const { registerNotification } = useNotificationService();
  const { formatMessage } = useIntl();
  const [isEmailResend, setIsEmailResend] = useState(false);

  const onResendVerificationMail = async () => {
    try {
      await sendEmailVerification();
      setIsEmailResend(true);
    } catch (error) {
      switch (error.code) {
        case AuthErrorCodes.NETWORK_REQUEST_FAILED:
          registerNotification({
            id: error.code,
            title: formatMessage({
              id: FirebaseAuthMessageId.NetworkFailure,
            }),
            isError: true,
          });
          break;
        case AuthErrorCodes.TOO_MANY_ATTEMPTS_TRY_LATER:
          registerNotification({
            id: error.code,
            title: formatMessage({
              id: FirebaseAuthMessageId.TooManyRequests,
            }),
            isError: true,
          });
          break;
        default:
          registerNotification({
            id: error.code,
            title: formatMessage({
              id: FirebaseAuthMessageId.DefaultError,
            }),
            isError: true,
          });
      }
    }
  };

  return (
    <InfoBox icon={faEnvelope} className={className}>
      <FormattedMessage id="credits.emailVerificationRequired" />{" "}
      {isEmailResend ? (
        <FormattedMessage id="credits.emailVerification.resendConfirmation" />
      ) : (
        <ResendEmailLink onClick={onResendVerificationMail}>
          <FormattedMessage id="credits.emailVerification.resend" />
        </ResendEmailLink>
      )}
    </InfoBox>
  );
};
