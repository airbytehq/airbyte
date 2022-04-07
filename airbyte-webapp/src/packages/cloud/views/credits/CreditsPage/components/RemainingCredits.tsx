import React, { useEffect, useRef, useState } from "react";
import { FormattedMessage, FormattedNumber } from "react-intl";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faStar } from "@fortawesome/free-regular-svg-icons";
import styled from "styled-components";
import { useSearchParams } from "react-router-dom";
import { useEffectOnce } from "react-use";

import { Button, LoadingButton } from "components";

import {
  useGetCloudWorkspace,
  useInvalidateCloudWorkspace,
} from "packages/cloud/services/workspaces/WorkspacesService";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useStripeCheckout } from "packages/cloud/services/stripe/StripeService";
import { CloudWorkspace } from "packages/cloud/lib/domain/cloudWorkspaces/types";
import { useConfig } from "config";

const Block = styled.div`
  background: ${({ theme }) => theme.darkBeigeColor};
  border-radius: 8px;
  padding: 18px 25px 22px;
  font-size: 13px;
  line-height: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
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
const StarIcon = styled(FontAwesomeIcon)`
  margin-right: 6px;
  font-size: 22px;
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

const RemainingCredits: React.FC = () => {
  const retryIntervalId = useRef<number>();
  const config = useConfig();
  const currentWorkspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(currentWorkspace.workspaceId);
  const [searchParams, setSearchParams] = useSearchParams();
  const invalidateWorkspace = useInvalidateCloudWorkspace(currentWorkspace.workspaceId);
  const { isLoading, mutateAsync: createCheckout } = useStripeCheckout();
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
    // Forward to stripe as soon as we created a checkout session successfully
    window.location.assign(stripeUrl);
  };

  return (
    <Block>
      <CreditView>
        <FormattedMessage id="credits.remainingCredits" />
        <Count>
          <StarIcon icon={faStar} />
          <FormattedNumber value={cloudWorkspace.remainingCredits} />
        </Count>
      </CreditView>
      <Actions>
        <LoadingButton
          size="xl"
          type="button"
          onClick={startStripeCheckout}
          isLoading={isLoading || isWaitingForCredits}
        >
          <FormattedMessage id="credits.buyCredits" />
        </LoadingButton>
        <Button as="a" target="_blank" href={config.ui.contactSales} size="xl">
          <FormattedMessage id="credits.talkToSales" />
        </Button>
      </Actions>
    </Block>
  );
};

export default RemainingCredits;
