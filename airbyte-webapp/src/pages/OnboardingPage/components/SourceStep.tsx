import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useFetcher } from "rest-hooks";

import ContentCard from "../../../components/ContentCard";
import ServiceForm from "../../../components/ServiceForm";
import SourceDefinitionSpecificationResource, {
  SourceDefinitionSpecification
} from "../../../core/resources/SourceDefinitionSpecification";
import { AnalyticsService } from "../../../core/analytics/AnalyticsService";
import config from "../../../config";
import PrepareDropDownLists from "./PrepareDropDownLists";
import { Source } from "../../../core/resources/Source";

type IProps = {
  source?: Source;
  onSubmit: (values: {
    name: string;
    serviceType: string;
    sourceDefinitionId?: string;
    connectionConfiguration?: any;
  }) => void;
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
  hasSuccess,
  errorStatus,
  source
}) => {
  const [sourceId, setSourceId] = useState("");
  const {
    sourceDefinitionSpecification,
    isLoading
  } = useSourceDefinitionSpecificationLoad(sourceId);
  const { getSourceDefinitionById } = PrepareDropDownLists();

  const onDropDownSelect = (sourceId: string) => {
    const sourceDefinition = getSourceDefinitionById(sourceId);

    AnalyticsService.track("New Source - Action", {
      airbyte_version: config.version,
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
