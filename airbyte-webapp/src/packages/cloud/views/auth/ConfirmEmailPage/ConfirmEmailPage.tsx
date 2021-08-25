import React from "react";
import styled from "styled-components";
import { FormattedHTMLMessage, FormattedMessage } from "react-intl";

import { FormTitle } from "../components/FormTitle";
import { H5 } from "components/base/Titles";
import { Link } from "components/Link";
import FormContent from "../components/FormContent";
import News from "../components/News";

type ConfirmEmailPageProps = {
  email: string;
};

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

const ConfirmEmailPage: React.FC<ConfirmEmailPageProps> = ({ email }) => {
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
            <Resend $light as="div">
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
