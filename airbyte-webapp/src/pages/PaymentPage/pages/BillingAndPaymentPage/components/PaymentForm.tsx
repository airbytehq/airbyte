import { useStripe, useElements } from "@stripe/react-stripe-js";
import React from "react";
import styled from "styled-components";

import { Input, Button } from "components";
import { Separator } from "components/Separator";

import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
import { SettingsRoute } from "pages/SettingsPage/SettingsPage";

import {
  StripeNumberInput,
  ExpiryCvcContainer,
  StripeExpiryInput,
  StripeCvcInput,
  StripeInputOptions,
} from "./StripeElements";

const FormContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  margin-left: 80px;
`;

const InputRow = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
`;

const InputContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
`;

const InputLabel = styled.label`
  font-weight: 500;
  font-size: 14px;
  line-height: 20px;
  color: #374151;
`;

const PaymentFormInput = styled(Input)`
  background-color: ${({ theme }) => theme.white};
  border-radius: 6px;
  padding: 11px 16px;
  line-height: 20px;
  border: 1px solid ${({ theme }) => theme.grey200};
  box-shadow: none;
  outline: none;
`;

const InputSeparator = styled.div`
  width: 40px;
`;

const FormFooter = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
`;

const ButtonTextContainer = styled.div`
  padding: 0 56px;
`;

const PaymentForm: React.FC = () => {
  const separatorHeight = "20px";
  const stripe = useStripe();
  const elements = useElements();
  const { push } = useRouter();

  const handleSubmit = (event: any) => {
    event.preventDefault();
    push(`/${RoutePaths.Settings}/${SettingsRoute.PlanAndBilling}`);
  };

  return (
    <FormContainer>
      <form onSubmit={handleSubmit}>
        <InputContainer>
          <InputLabel>Name on card</InputLabel>
          <PaymentFormInput focusedStyle={false} />
        </InputContainer>
        <Separator height={separatorHeight} />

        <InputLabel>Card details</InputLabel>
        <StripeNumberInput options={StripeInputOptions} />
        <ExpiryCvcContainer>
          <StripeExpiryInput options={StripeInputOptions} />
          <StripeCvcInput options={StripeInputOptions} />
        </ExpiryCvcContainer>
        <Separator height={separatorHeight} />

        <InputRow>
          <InputContainer>
            <InputLabel>Company name</InputLabel>
            <PaymentFormInput focusedStyle={false} />
          </InputContainer>
          <InputSeparator />
          <InputContainer>
            <InputLabel>Billing email</InputLabel>
            <PaymentFormInput focusedStyle={false} />
          </InputContainer>
        </InputRow>
        <Separator height={separatorHeight} />

        <InputContainer>
          <InputLabel>Address</InputLabel>
          <PaymentFormInput focusedStyle={false} />
        </InputContainer>
        <Separator height={separatorHeight} />

        <InputRow>
          <InputContainer>
            <InputLabel>Postal code</InputLabel>
            <PaymentFormInput focusedStyle={false} />
          </InputContainer>
          <InputSeparator />
          <InputContainer>
            <InputLabel>City</InputLabel>
            <PaymentFormInput focusedStyle={false} />
          </InputContainer>
        </InputRow>
        <Separator height={separatorHeight} />

        <InputRow>
          <InputContainer>
            <InputLabel>Country</InputLabel>
            <PaymentFormInput focusedStyle={false} />
          </InputContainer>
          <InputSeparator />
          <InputContainer>
            <InputLabel>VAT number (optional)</InputLabel>
            <PaymentFormInput focusedStyle={false} />
          </InputContainer>
        </InputRow>
        <Separator height={separatorHeight} />

        <FormFooter>
          <Button size="xl" type="submit" disabled={!stripe || !elements}>
            <ButtonTextContainer>Pay</ButtonTextContainer>
          </Button>
        </FormFooter>
      </form>
    </FormContainer>
  );
};

export default PaymentForm;
