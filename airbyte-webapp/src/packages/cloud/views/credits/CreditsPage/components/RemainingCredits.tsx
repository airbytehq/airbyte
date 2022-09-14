import React, { useEffect, useRef, useState } from "react";
import { FormattedMessage, FormattedNumber } from "react-intl";
import { useSearchParams } from "react-router-dom";
import { useEffectOnce } from "react-use";
import styled from "styled-components";

import { Button, LoadingButton } from "components";

import { useConfig } from "config";
import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { CloudWorkspace } from "packages/cloud/lib/domain/cloudWorkspaces/types";
import { useStripeCheckout } from "packages/cloud/services/stripe/StripeService";
import {
  useGetCloudWorkspace,
  useInvalidateCloudWorkspace,
} from "packages/cloud/services/workspaces/WorkspacesService";

interface Props {
  selfServiceCheckoutEnabled: boolean;
}

const Block = styled.div`
  background: ${({ theme }) => theme.darkBeigeColor};
  border-radius: 8px;
  padding: 18px 25px 22px;
  font-size: 13px;
  line-height: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 10px 0px;
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
  const config = useConfig();
  const currentWorkspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(currentWorkspace.workspaceId);
  const [searchParams, setSearchParams] = useSearchParams();
  const invalidateWorkspace = useInvalidateCloudWorkspace(currentWorkspace.workspaceId);
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
          invalidateWorkspace();
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
    });
    await analytics.track(Namespace.CREDITS, Action.CHECKOUT_START, {
      actionDescription: "Checkout Start",
    });
    // Forward to stripe as soon as we created a checkout session successfully
    window.location.assign(stripeUrl);
  };

  return (
    <Block>
      <CreditView>
        <FormattedMessage id="credits.remainingCredits" />
        <Count>
          <FormattedNumber value={cloudWorkspace.remainingCredits} />
        </Count>
      </CreditView>
      <Actions>
        <LoadingButton
          disabled={!selfServiceCheckoutEnabled}
          type="button"
          onClick={startStripeCheckout}
          isLoading={isLoading || isWaitingForCredits}
        >
          <FormattedMessage id="credits.buyCredits" />
        </LoadingButton>
        <Button as="a" target="_blank" href={config.links.contactSales}>
          <FormattedMessage id="credits.talkToSales" />
        </Button>
      </Actions>
    </Block>
  );
};

export default RemainingCredits;
