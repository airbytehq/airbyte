import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useFetcher } from "rest-hooks";

import ConnectionBlock from "../../../../../components/ConnectionBlock";
import ContentCard from "../../../../../components/ContentCard";
import ServiceForm from "../../../../../components/ServiceForm";
import { DestinationDefinition } from "../../../../../core/resources/DestinationDefinition";
import SourceDefinitionSpecificationResource, {
  SourceDefinitionSpecification
} from "../../../../../core/resources/SourceDefinitionSpecification";
import { AnalyticsService } from "../../../../../core/analytics/AnalyticsService";
import config from "../../../../../config";
import useRouter from "../../../../../components/hooks/useRouterHook";

type IProps = {
  onSubmit: (values: {
    name: string;
    serviceType: string;
    sourceDefinitionId?: string;
    connectionConfiguration?: any;
  }) => void;
  destinationDefinition: DestinationDefinition;
  dropDownData: Array<{ text: string; value: string; img?: string }>;
  hasSuccess?: boolean;
  errorStatus?: number;
};

const useSourceDefinitionSpecificationLoad = (sourceDefinitionId: string) => {
  const [
    sourceDefinitionSpecification,
    setSourceDefinitionSpecification
  ] = useState<null | SourceDefinitionSpecification>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchSourceDefinitionSpecification = useFetcher(
    SourceDefinitionSpecificationResource.detailShape(),
    true
  );

  useEffect(() => {
    (async () => {
      if (sourceDefinitionId) {
        setIsLoading(true);
        setSourceDefinitionSpecification(
          await fetchSourceDefinitionSpecification({ sourceDefinitionId })
        );
        setIsLoading(false);
      }
    })();
  }, [fetchSourceDefinitionSpecification, sourceDefinitionId]);

  return { sourceDefinitionSpecification, isLoading };
};

const SourceStep: React.FC<IProps> = ({
  onSubmit,
  dropDownData,
  destinationDefinition,
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
      <ConnectionBlock itemTo={{ name: destinationDefinition.name }} />
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

export default SourceStep;
