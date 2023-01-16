import React from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";

import { CloudInviteUsersHint } from "components/CloudInviteUsersHint";
import { HeadTitle } from "components/common/HeadTitle";
import { FormPageContent } from "components/ConnectorBlocks";
import { DestinationForm } from "components/destination/DestinationForm";
import { PageHeader } from "components/ui/PageHeader";

import { ConnectionConfiguration } from "core/domain/connection";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useCreateDestination } from "hooks/services/useDestinationHook";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout";

export const CreateDestinationPage: React.FC = () => {
  useTrackPage(PageTrackingCodes.DESTINATION_NEW);

  const navigate = useNavigate();
  const { destinationDefinitions } = useDestinationDefinitionList();
  const { mutateAsync: createDestination } = useCreateDestination();

  const onSubmitDestinationForm = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    const connector = destinationDefinitions.find((item) => item.destinationDefinitionId === values.serviceType);
    const result = await createDestination({
      values,
      destinationConnector: connector,
    });
    setTimeout(() => {
      navigate(`../${result.destinationId}`);
    }, 2000);
  };

  return (
    <>
      <HeadTitle titles={[{ id: "destinations.newDestinationTitle" }]} />
      <ConnectorDocumentationWrapper>
        <PageHeader title={null} middleTitleBlock={<FormattedMessage id="destinations.newDestinationTitle" />} />
        <FormPageContent>
          <DestinationForm onSubmit={onSubmitDestinationForm} destinationDefinitions={destinationDefinitions} />
          <CloudInviteUsersHint connectorType="destination" />
        </FormPageContent>
      </ConnectorDocumentationWrapper>
    </>
  );
};
