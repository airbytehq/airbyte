import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import ContentCard from "../../../../../components/ContentCard";
import ServiceForm from "../../../../../components/ServiceForm";
import { AnalyticsService } from "../../../../../core/analytics/AnalyticsService";
import config from "../../../../../config";
import useRouter from "../../../../../components/hooks/useRouterHook";
import { useSourceDefinitionSpecificationLoad } from "../../../../../components/hooks/services/useSourceHook";
import { IDataItem } from "../../../../../components/DropDown/components/ListItem";

type IProps = {
  onSubmit: (values: {
    name: string;
    serviceType: string;
    sourceDefinitionId?: string;
    connectionConfiguration?: any;
  }) => void;
  dropDownData: IDataItem[];
  hasSuccess?: boolean;
  errorStatus?: number;
};

const SourceForm: React.FC<IProps> = ({
  onSubmit,
  dropDownData,
  errorStatus,
  hasSuccess
}) => {
  const { location }: any = useRouter();

  const [sourceDefinitionId, setSourceDefinitionId] = useState(
    location.state?.sourceDefinitionId || ""
  );
  const {
    sourceDefinitionSpecification,
    isLoading
  } = useSourceDefinitionSpecificationLoad(sourceDefinitionId);
  const onDropDownSelect = (sourceDefinitionId: string) => {
    setSourceDefinitionId(sourceDefinitionId);
    const connector = dropDownData.find(
      item => item.value === sourceDefinitionId
    );

    AnalyticsService.track("New Source - Action", {
      user_id: config.ui.workspaceId,
      action: "Select a connector",
      connector_source_definition: connector?.text,
      connector_source_definition_id: sourceDefinitionId
    });
  };

  const onSubmitForm = async (values: {
    name: string;
    serviceType: string;
  }) => {
    await onSubmit({
      ...values,
      sourceDefinitionId: sourceDefinitionSpecification?.sourceDefinitionId
    });
  };

  const errorMessage =
    errorStatus === 0 ? null : errorStatus === 400 ? (
      <FormattedMessage id="form.validationError" />
    ) : (
      <FormattedMessage id="form.someError" />
    );

  return (
    <>
      <ContentCard title={<FormattedMessage id="onboarding.sourceSetUp" />}>
        <ServiceForm
          onDropDownSelect={onDropDownSelect}
          onSubmit={onSubmitForm}
          formType="source"
          dropDownData={dropDownData}
          specifications={
            sourceDefinitionSpecification?.connectionSpecification
          }
          hasSuccess={hasSuccess}
          errorMessage={errorMessage}
          isLoading={isLoading}
          formValues={
            sourceDefinitionId
              ? { serviceType: sourceDefinitionId, name: "" }
              : undefined
          }
          allowChangeConnector
        />
      </ContentCard>
    </>
  );
};

export default SourceForm;
