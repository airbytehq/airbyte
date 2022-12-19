import { CardNumberElement, CardExpiryElement, CardCvcElement } from "@stripe/react-stripe-js";
import styled from "styled-components";
import { theme } from "theme";

const StripeElementStyle = `
    width: 100%;
    padding: 11px 16px;
    background-color: ${theme.white};
`;

export const StripeNumberInput = styled(CardNumberElement)`
  ${StripeElementStyle}
  border-radius: 6px 6px 0 0;
  border: 1px solid ${theme.grey200};
`;

export const ExpiryCvcContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
`;

export const StripeExpiryInput = styled(CardExpiryElement)`
  ${StripeElementStyle}
  border-radius: 0 0 0 6px;
  border-right: 1px solid ${theme.grey200};
  border-bottom: 1px solid ${theme.grey200};
  border-left: 1px solid ${theme.grey200};
`;

export const StripeCvcInput = styled(CardCvcElement)`
  ${StripeElementStyle}
  border-radius: 0 0 6px 0;
  border-right: 1px solid ${theme.grey200};
  border-bottom: 1px solid ${theme.grey200};
`;

export const StripeInputOptions = {
  style: {
    base: {
      fontWeight: 400,
      fontSize: "14px",
      lineHeight: "20px",
      "::placeholder": {
        fontSize: "12px",
        color: `${theme.grey200}`,
      },
      ":focus": {
        color: theme.black300,
        border: `1px solid ${theme.blue}`,
      },
    },
    empty: {
      color: `${theme.grey200}`,
      "::placeholder": {
        color: `${theme.grey200}`,
      },
      ":focus": {
        color: theme.black300,
        border: `1px solid ${theme.blue}`,
      },
    },
    invalid: {
      color: theme.red,
    },
    complete: {
      color: theme.black300,
    },
  },
};
