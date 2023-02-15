import React, { Suspense, useMemo } from "react";
import { useIntl } from "react-intl";
import { Outlet, useNavigate, useParams } from "react-router-dom";

import { ApiErrorBoundary } from "components/common/ApiErrorBoundary";
import { HeadTitle } from "components/common/HeadTitle";
import { ItemTabs, StepsTypes } from "components/ConnectorBlocks";
import LoadingPage from "components/LoadingPage";
import { Breadcrumbs } from "components/ui/Breadcrumbs";
import { PageHeader } from "components/ui/PageHeader";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout";

import { useSetupSourceOverviewContext } from "../SourceOverviewPage/sourceOverviewContext";

const SourceItemPage: React.FC = () => {
  useTrackPage(PageTrackingCodes.SOURCE_ITEM);
  const params = useParams<{ "*": StepsTypes | "" | undefined; id: string }>();
  const navigate = useNavigate();
  const { formatMessage } = useIntl();
  const currentStep = useMemo<StepsTypes | "" | undefined>(
    () => (params["*"] === "" ? StepsTypes.OVERVIEW : params["*"]),
    [params]
  );

  const { source, sourceDefinition, connections } = useSetupSourceOverviewContext(params.id ?? "");

  const breadcrumbsData = [
    {
      label: formatMessage({ id: "sidebar.sources" }),
      to: "..",
    },
    { label: source.name },
  ];

  const onSelectStep = (id: string) => {
    const path = id === StepsTypes.OVERVIEW ? "." : id.toLowerCase();
    navigate(path);
  };

  return (
    <ConnectorDocumentationWrapper>
      <HeadTitle titles={[{ id: "admin.sources" }, { title: source.name }]} />
      <PageHeader
        title={<Breadcrumbs data={breadcrumbsData} />}
        middleComponent={<ItemTabs currentStep={currentStep} setCurrentStep={onSelectStep} />}
      />

      <Suspense fallback={<LoadingPage />}>
        <ApiErrorBoundary>
          <Outlet context={{ source, sourceDefinition, connections }} />
        </ApiErrorBoundary>
      </Suspense>
    </ConnectorDocumentationWrapper>
  );
};

export default SourceItemPage;
