import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";

import ContentCard from "../../../components/ContentCard";
import ServiceForm from "../../../components/ServiceForm";
import { AnalyticsService } from "../../../core/analytics/AnalyticsService";
import { Source } from "../../../core/resources/Source";

import { useSourceDefinitionSpecificationLoad } from "../../../components/hooks/services/useSourceHook";

import usePrepareDropdownLists from "./usePrepareDropdownLists";

import config from "../../../config";
import { IDataItem } from "../../../components/DropDown/components/ListItem";

type IProps = {
  source?: Source;
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

const SourceStep: React.FC<IProps> = ({
  onSubmit,
  dropDownData,
  hasSuccess,
  errorStatus,
  source
}) => {
  const [sourceId, setSourceId] = useState("");
  const {
    sourceDefinitionSpecification,
    isLoading
  } = useSourceDefinitionSpecificationLoad(sourceId);
  const { getSourceDefinitionById } = usePrepareDropdownLists();

  const onDropDownSelect = (sourceId: string) => {
    const sourceDefinition = getSourceDefinitionById(sourceId);

    AnalyticsService.track("New Source - Action", {
      user_id: config.ui.workspaceId,
      action: "Select a connector",
      connector_source: sourceDefinition?.name,
      connector_source_id: sourceDefinition?.sourceDefinitionId
    });

    setSourceId(sourceId);
  };
  const onSubmitForm = async (values: { name: string; serviceType: string }) =>
    onSubmit({
      ...values,
      sourceDefinitionId: sourceDefinitionSpecification?.sourceDefinitionId
    });

  const errorMessage =
    errorStatus === 0 ? null : errorStatus === 400 ? (
      <FormattedMessage id="form.validationError" />
    ) : (
      <FormattedMessage id="form.someError" />
    );

  useEffect(() => setSourceId(source?.sourceDefinitionId || ""), [source]);

  return (
    <ContentCard title={<FormattedMessage id="onboarding.sourceSetUp" />}>
      <ServiceForm
        allowChangeConnector
        onDropDownSelect={onDropDownSelect}
        onSubmit={onSubmitForm}
        formType="source"
        dropDownData={dropDownData}
        hasSuccess={hasSuccess}
        errorMessage={errorMessage}
        specifications={sourceDefinitionSpecification?.connectionSpecification}
        documentationUrl={sourceDefinitionSpecification?.documentationUrl}
        isLoading={isLoading}
        formValues={source}
      />
    </ContentCard>
  );
};

export default SourceStep;
