import React from "react";
import styled from "styled-components";
import { FormattedHTMLMessage, FormattedMessage, useIntl } from "react-intl";

import { AuthErrorCodes } from "firebase/auth";

import { H5, Link } from "components";
import { FormTitle } from "../components/FormTitle";
import FormContent from "../components/FormContent";
import News from "../components/News";
import {
  useAuthService,
  useCurrentUser,
} from "packages/cloud/services/auth/AuthService";
import { useNotificationService } from "hooks/services/Notification/NotificationService";

const Text = styled(H5)`
  padding: 27px 0 30px;
  margin-right: -40px;
`;

const Resend = styled(Link)`
  cursor: pointer;
`;

const TitleBlock = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const Img = styled.img`
  margin: -5px 0 0 30px;
`;

const Content = styled.div`
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: row;
  background: ${({ theme }) => theme.whiteColor};
`;

const Part = styled.div`
  flex: 1 0 0;
  padding: 20px 36px 39px 46px;
  height: 100%;
`;

const NewsPart = styled(Part)`
  background: ${({ theme }) => theme.beigeColor};
  padding: 36px 97px 39px 64px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
`;

enum FirebaseAuthMessageId {
  Success = "firebase.auth.success",
  NetworkFailure = "firebase.auth.error.networkRequestFailed",
  TooManyRequests = "firebase.auth.error.tooManyRequests",
  DefaultError = "firebase.auth.error.default",
}

const ConfirmEmailPage: React.FC = () => {
  const { sendEmailVerification } = useAuthService();
  const { email } = useCurrentUser();
  const { registerNotification } = useNotificationService();
  const { formatMessage } = useIntl();

  const onClickSendEmailVerification = () => {
    sendEmailVerification()
      .then(() => {
        registerNotification({
          id: "auth/success",
          title: formatMessage({ id: FirebaseAuthMessageId.Success }),
          isError: false,
        });
      })
      .catch((error) => {
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
      });
  };

  return (
    <Content>
      <Part>
        <FormContent toLogin={false}>
          <div>
            <TitleBlock>
              <div>
                <FormTitle bold>
                  <FormattedMessage id="login.lastStep" />
                </FormTitle>
                <H5>
                  <FormattedMessage id="login.confirmEmail" />
                </H5>
              </div>
              <Img src="/newsletter.png" height={68} />
            </TitleBlock>
            <Text>
              <FormattedHTMLMessage
                id="login.confirmEmail.text"
                values={{ email }}
              />
            </Text>
            <Resend $light as="div" onClick={onClickSendEmailVerification}>
              <FormattedMessage id="login.resendEmail" />
            </Resend>
          </div>
        </FormContent>
      </Part>
      <NewsPart>
        <News />
      </NewsPart>
    </Content>
  );
};
export default ConfirmEmailPage;
