import React from "react";
import styled from "styled-components";
import { FormattedHTMLMessage, FormattedMessage } from "react-intl";

import { FormTitle } from "../components/FormTitle";
import { H5 } from "components/base/Titles";
import { Link } from "components/Link";

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

const ConfirmEmailPage: React.FC<ConfirmEmailPageProps> = ({ email }) => {
  return (
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
        <FormattedHTMLMessage id="login.confirmEmail.text" values={{ email }} />
      </Text>
      <Resend $light as="div">
        <FormattedMessage id="login.resendEmail" />
      </Resend>
    </div>
  );
};
export default ConfirmEmailPage;
