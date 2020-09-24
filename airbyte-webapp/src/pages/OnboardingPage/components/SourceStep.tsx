import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useFetcher } from "rest-hooks";

import ContentCard from "../../../components/ContentCard";
import ServiceForm from "../../../components/ServiceForm";
import SourceSpecificationResource, {
  SourceSpecification
} from "../../../core/resources/SourceSpecification";
import { AnalyticsService } from "../../../core/analytics/AnalyticsService";
import config from "../../../config";
import PrepareDropDownLists from "./PrepareDropDownLists";

type IProps = {
  onSubmit: (values: {
    name: string;
    serviceType: string;
    specificationId?: string;
    connectionConfiguration?: any;
  }) => void;
  dropDownData: Array<{ text: string; value: string; img?: string }>;
  hasSuccess?: boolean;
  errorStatus?: number;
};

const useSourceSpecificationLoad = (sourceId: string) => {
  const [
    sourceSpecification,
    setSourceSpecification
  ] = useState<null | SourceSpecification>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchSourceSpecification = useFetcher(
    SourceSpecificationResource.detailShape(),
    true
  );

  useEffect(() => {
    (async () => {
      if (sourceId) {
        setIsLoading(true);
        setSourceSpecification(await fetchSourceSpecification({ sourceId }));
        setIsLoading(false);
      }
    })();
  }, [fetchSourceSpecification, sourceId]);

  return { sourceSpecification, isLoading };
};

const SourceStep: React.FC<IProps> = ({
  onSubmit,
  dropDownData,
  hasSuccess,
  errorStatus
}) => {
  const [sourceId, setSourceId] = useState("");
  const { sourceSpecification, isLoading } = useSourceSpecificationLoad(
    sourceId
  );
  const { getSourceById } = PrepareDropDownLists();

  const onDropDownSelect = (sourceId: string) => {
    const connector = getSourceById(sourceId);

    AnalyticsService.track("New Source - Action", {
      user_id: config.ui.workspaceId,
      action: "Select a connector",
      connector_source: connector?.name,
      connector_source_id: connector?.sourceId
    });

    setSourceId(sourceId);
  };
  const onSubmitForm = async (values: {
    name: string;
    serviceType: string;
  }) => {
    await onSubmit({
      ...values,
      specificationId: sourceSpecification?.sourceSpecificationId
    });
  };

  const errorMessage =
    errorStatus === 0 ? null : errorStatus === 400 ? (
      <FormattedMessage id="form.validationError" />
    ) : (
      <FormattedMessage id="form.someError" />
    );

  return (
    <ContentCard title={<FormattedMessage id="onboarding.sourceSetUp" />}>
      <ServiceForm
        onDropDownSelect={onDropDownSelect}
        onSubmit={onSubmitForm}
        formType="source"
        dropDownData={dropDownData}
        hasSuccess={hasSuccess}
        errorMessage={errorMessage}
        specifications={sourceSpecification?.connectionSpecification}
        documentationUrl={sourceSpecification?.documentationUrl}
        isLoading={isLoading}
      />
    </ContentCard>
  );
};

export default SourceStep;
