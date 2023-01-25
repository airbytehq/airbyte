import React, { Suspense, useMemo } from "react";
import { useIntl } from "react-intl";
import { Outlet, useNavigate, useParams } from "react-router-dom";

import { LoadingPage } from "components";
import { ApiErrorBoundary } from "components/common/ApiErrorBoundary";
import { HeadTitle } from "components/common/HeadTitle";
import { ItemTabs, StepsTypes } from "components/ConnectorBlocks";
import { Breadcrumbs } from "components/ui/Breadcrumbs";
import { PageHeader } from "components/ui/PageHeader";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout";

import { useGetDestination } from "../../../hooks/services/useDestinationHook";

export const DestinationItemPage: React.FC = () => {
  useTrackPage(PageTrackingCodes.DESTINATION_ITEM);
  const params = useParams() as { "*": StepsTypes | ""; id: string };
  const navigate = useNavigate();
  const { formatMessage } = useIntl();
  const currentStep = useMemo<string>(() => (params["*"] === "" ? StepsTypes.OVERVIEW : params["*"]), [params]);

  const destination = useGetDestination(params.id);

  const onSelectStep = (id: string) => {
    const path = id === StepsTypes.OVERVIEW ? "." : id.toLowerCase();
    navigate(path);
  };

  const breadcrumbsData = [
    {
      label: formatMessage({ id: "admin.destinations" }),
      to: "..",
    },
    { label: destination.name },
  ];

  return (
    <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>
      <ConnectorDocumentationWrapper>
        <HeadTitle titles={[{ id: "admin.destinations" }, { title: destination.name }]} />
        <PageHeader
          title={<Breadcrumbs data={breadcrumbsData} />}
          middleComponent={<ItemTabs currentStep={currentStep} setCurrentStep={onSelectStep} />}
        />
        <Suspense fallback={<LoadingPage />}>
          <ApiErrorBoundary>
            <Outlet />
          </ApiErrorBoundary>
        </Suspense>
      </ConnectorDocumentationWrapper>
    </ResourceNotFoundErrorBoundary>
  );
};
