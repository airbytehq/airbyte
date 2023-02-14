import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useEffect, useRef, useState } from "react";
import { FormattedMessage, FormattedNumber } from "react-intl";
import { useSearchParams } from "react-router-dom";
import { useEffectOnce } from "react-use";
import styled from "styled-components";

import { Button } from "components/ui/Button";

import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { CloudWorkspace } from "packages/cloud/lib/domain/cloudWorkspaces/types";
import { useStripeCheckout } from "packages/cloud/services/stripe/StripeService";
import {
  useGetCloudWorkspace,
  useInvalidateCloudWorkspace,
} from "packages/cloud/services/workspaces/CloudWorkspacesService";
import { links } from "utils/links";

import { LowCreditBalanceHint } from "./LowCreditBalanceHint";

interface Props {
  selfServiceCheckoutEnabled: boolean;
}

const Block = styled.div`
  background: ${({ theme }) => theme.blue50};
  border-radius: 8px;
  padding: 15px 20px;
  font-size: 13px;
  line-height: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 10px 0;
`;
const CreditView = styled.div`
  text-transform: uppercase;
`;
const Count = styled.div`
  padding-top: 6px;
  font-weight: bold;
  font-size: 24px;
  line-height: 29px;
`;
const Actions = styled.div`
  display: flex;
  gap: 12px;
`;

const STRIPE_SUCCESS_QUERY = "stripeCheckoutSuccess";

/**
 * Checks whether the given cloud workspace had a recent increase in credits.
 */
function hasRecentCreditIncrease(cloudWorkspace: CloudWorkspace): boolean {
  const lastIncrement = cloudWorkspace.lastCreditPurchaseIncrementTimestamp;
  return lastIncrement ? Date.now() - lastIncrement < 30000 : false;
}

const RemainingCredits: React.FC<Props> = ({ selfServiceCheckoutEnabled }) => {
  const retryIntervalId = useRef<number>();
  const currentWorkspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(currentWorkspace.workspaceId);
  const [searchParams, setSearchParams] = useSearchParams();
  const invalidateCloudWorkspace = useInvalidateCloudWorkspace(currentWorkspace.workspaceId);
  const { isLoading, mutateAsync: createCheckout } = useStripeCheckout();
  const analytics = useAnalyticsService();
  const [isWaitingForCredits, setIsWaitingForCredits] = useState(false);

  useEffectOnce(() => {
    // If we are coming back from a successfull stripe checkout ...
    if (searchParams.has(STRIPE_SUCCESS_QUERY)) {
      // Remove the stripe parameter from the URL
      setSearchParams({}, { replace: true });
      // If the workspace doesn't have a recent increase in credits our server has not yet
      // received the Stripe callback or updated the workspace information. We're going to
      // switch into a loading mode and relaod the workspace every 3s from now on until
      // the workspace has received the credit update (see useEffect below)
      if (!hasRecentCreditIncrease(cloudWorkspace)) {
        setIsWaitingForCredits(true);
        retryIntervalId.current = window.setInterval(() => {
          invalidateCloudWorkspace();
        }, 3000);
      }
    }

    return () => clearInterval(retryIntervalId.current);
  });

  useEffect(() => {
    // Whenever the `cloudWorkspace` changes and now has a recent credit increment, while we're still waiting
    // for new credits to come in (i.e. the retryIntervalId is still set), we know that we now
    // handled the actual credit purchase and can clean the interval and loading state.
    if (retryIntervalId.current && hasRecentCreditIncrease(cloudWorkspace)) {
      clearInterval(retryIntervalId.current);
      retryIntervalId.current = undefined;
      setIsWaitingForCredits(false);
    }
  }, [cloudWorkspace]);

  const startStripeCheckout = async () => {
    // Use the current URL as a success URL but attach the STRIPE_SUCCESS_QUERY to it
    const successUrl = new URL(window.location.href);
    successUrl.searchParams.set(STRIPE_SUCCESS_QUERY, "true");
    const { stripeUrl } = await createCheckout({
      workspaceId: currentWorkspace.workspaceId,
      successUrl: successUrl.href,
      cancelUrl: window.location.href,
      stripeMode: "payment",
    });
    analytics.track(Namespace.CREDITS, Action.CHECKOUT_START, {
      actionDescription: "Checkout Start",
    });
    // Forward to stripe as soon as we created a checkout session successfully
    window.location.assign(stripeUrl);
  };

  return (
    <>
      <LowCreditBalanceHint>
        <Button
          disabled={!selfServiceCheckoutEnabled}
          type="button"
          size="xs"
          variant="dark"
          onClick={startStripeCheckout}
          isLoading={isLoading || isWaitingForCredits}
          icon={<FontAwesomeIcon icon={faPlus} />}
        >
          <FormattedMessage id="credits.buyCredits" />
        </Button>
      </LowCreditBalanceHint>
      <Block>
        <CreditView>
          <FormattedMessage id="credits.remainingCredits" />
          <Count>
            <FormattedNumber
              value={cloudWorkspace.remainingCredits}
              maximumFractionDigits={2}
              minimumFractionDigits={2}
            />
          </Count>
        </CreditView>
        <Actions>
          <Button
            disabled={!selfServiceCheckoutEnabled}
            type="button"
            size="xs"
            onClick={startStripeCheckout}
            isLoading={isLoading || isWaitingForCredits}
            icon={<FontAwesomeIcon icon={faPlus} />}
          >
            <FormattedMessage id="credits.buyCredits" />
          </Button>
          <Button size="xs" onClick={() => window.open(links.contactSales, "_blank")}>
            <FormattedMessage id="credits.talkToSales" />
          </Button>
        </Actions>
      </Block>
    </>
  );
};

export default RemainingCredits;
