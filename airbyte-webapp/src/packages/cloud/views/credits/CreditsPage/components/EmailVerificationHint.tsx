import { faEnvelope } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Callout } from "components/ui/Callout";

import { useAuthService } from "packages/cloud/services/auth/AuthService";

interface Props {
  className?: string;
}

const ResendEmailLink = styled.button`
  appearance: none;
  background: none;
  border: none;
  font-size: inherit;
  text-decoration: underline;
  cursor: pointer;
  padding: 0;
  margin: 0;
  display: inline;
  color: ${({ theme }) => theme.mediumPrimaryColor};
`;

export const EmailVerificationHint: React.FC<Props> = ({ className }) => {
  const { sendEmailVerification } = useAuthService();
  const [isEmailResend, setIsEmailResend] = useState(false);

  const onResendVerificationMail = async () => {
    // the shared error handling inside `sendEmailVerification` suffices
    await sendEmailVerification();
    setIsEmailResend(true);
  };

  return (
    <Callout className={className}>
      <FontAwesomeIcon icon={faEnvelope} size="lg" />
      <FormattedMessage id="credits.emailVerificationRequired" />{" "}
      {isEmailResend ? (
        <FormattedMessage id="credits.emailVerification.resendConfirmation" />
      ) : (
        <ResendEmailLink onClick={onResendVerificationMail}>
          <FormattedMessage id="credits.emailVerification.resend" />
        </ResendEmailLink>
      )}
    </Callout>
  );
};
