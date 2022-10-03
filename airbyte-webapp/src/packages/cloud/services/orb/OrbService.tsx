import { useMemo } from "react";
import { useMutation, useQuery } from "react-query";

import { AddTrialCreditsRequest, OrbService } from "packages/cloud/lib/domain/orb/OrbService";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

import { useGetCloudWorkspace } from "../workspaces/CloudWorkspacesService";

export const useAddTrialCreditsMutation = () => {
  const service = useMemo(() => new OrbService(), []);
  const workspace = useCurrentWorkspace();
  const { trialExpiryTimestamp } = useGetCloudWorkspace(workspace.workspaceId);
  const expiry_date = trialExpiryTimestamp ? new Date(trialExpiryTimestamp).toISOString().slice(0, 10) : undefined;

  const customerIdQuery = useQuery("orb-customer-id", () => service.getCustomerIdByExternalId(workspace.workspaceId), {
    select: (data) => ({ customerId: data.id }),
  });

  const customerId = customerIdQuery.data?.customerId ?? "";

  return useMutation(({ amount }: Pick<AddTrialCreditsRequest, "amount">) =>
    service.addTrialCredits({
      amount,
      customerId,
      expiry_date,
    })
  );
};
