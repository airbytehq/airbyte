import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";
import { Separator } from "components/Separator";

import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
import { SettingsRoute } from "pages/SettingsPage/SettingsPage";

const Container = styled.div`
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  font-size: 28px;
`;

const PaymentErrorPage: React.FC = () => {
  const { push } = useRouter();
  return (
    <Container>
      <FormattedMessage id="payment.error.text" />
      <Separator />
      <Button
        size="lg"
        onClick={() => {
          push(`/${RoutePaths.Settings}/${SettingsRoute.PlanAndBilling}`);
        }}
      >
        <FormattedMessage id="payment.errorPage.btnText" />
      </Button>
    </Container>
  );
};

export default PaymentErrorPage;
