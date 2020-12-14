import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import ContentCard from "../../../../../components/ContentCard";
import ServiceForm from "../../../../../components/ServiceForm";
import { AnalyticsService } from "../../../../../core/analytics/AnalyticsService";
import config from "../../../../../config";
import useRouter from "../../../../../components/hooks/useRouterHook";
import { useDestinationDefinitionSpecificationLoad } from "../../../../../components/hooks/services/useDestinationHook";
import { IDataItem } from "../../../../../components/DropDown/components/ListItem";

type IProps = {
  onSubmit: (values: {
    name: string;
    serviceType: string;
    destinationDefinitionId?: string;
    connectionConfiguration?: any;
  }) => void;
  dropDownData: IDataItem[];
  hasSuccess?: boolean;
  errorStatus?: number;
};

const DestinationForm: React.FC<IProps> = ({
  onSubmit,
  dropDownData,
  errorStatus,
  hasSuccess
}) => {
  const { location }: any = useRouter();

  const [destinationDefinitionId, setDestinationDefinitionId] = useState(
    location.state?.destinationDefinitionId || ""
  );
  const {
    destinationDefinitionSpecification,
    isLoading
  } = useDestinationDefinitionSpecificationLoad(destinationDefinitionId);
  const onDropDownSelect = (destinationDefinitionId: string) => {
    setDestinationDefinitionId(destinationDefinitionId);
    const connector = dropDownData.find(
      item => item.value === destinationDefinitionId
    );

    AnalyticsService.track("New Destination - Action", {
      user_id: config.ui.workspaceId,
      action: "Select a connector",
      connector_destination_definition: connector?.text,
      connector_destination_definition_id: destinationDefinitionId
    });
  };

  const onSubmitForm = async (values: {
    name: string;
    serviceType: string;
  }) => {
    await onSubmit({
      ...values,
      destinationDefinitionId:
        destinationDefinitionSpecification?.destinationDefinitionId
    });
  };

  const errorMessage =
    errorStatus === 0 ? null : errorStatus === 400 ? (
      <FormattedMessage id="form.validationError" />
    ) : (
      <FormattedMessage id="form.someError" />
    );

  return (
    <ContentCard title={<FormattedMessage id="onboarding.destinationSetUp" />}>
      <ServiceForm
        onDropDownSelect={onDropDownSelect}
        onSubmit={onSubmitForm}
        formType="destination"
        dropDownData={dropDownData}
        specifications={
          destinationDefinitionSpecification?.connectionSpecification
        }
        hasSuccess={hasSuccess}
        errorMessage={errorMessage}
        isLoading={isLoading}
        formValues={
          destinationDefinitionId
            ? { serviceType: destinationDefinitionId, name: "" }
            : undefined
        }
        allowChangeConnector
      />
    </ContentCard>
  );
};

export default DestinationForm;
