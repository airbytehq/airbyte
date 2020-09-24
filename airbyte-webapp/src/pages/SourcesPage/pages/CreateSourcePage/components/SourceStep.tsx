import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useFetcher } from "rest-hooks";

import ConnectionBlock from "../../../../../components/ConnectionBlock";
import ContentCard from "../../../../../components/ContentCard";
import ServiceForm from "../../../../../components/ServiceForm";
import { Destination } from "../../../../../core/resources/Destination";
import SourceSpecificationResource, {
  SourceSpecification
} from "../../../../../core/resources/SourceSpecification";
import { AnalyticsService } from "../../../../../core/analytics/AnalyticsService";
import config from "../../../../../config";

type IProps = {
  onSubmit: (values: {
    name: string;
    serviceType: string;
    specificationId?: string;
    connectionConfiguration?: any;
  }) => void;
  destination: Destination;
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

const CreateSourcePage: React.FC<IProps> = ({
  onSubmit,
  dropDownData,
  destination,
  errorStatus,
  hasSuccess
}) => {
  const [sourceId, setSourceId] = useState("");
  const { sourceSpecification, isLoading } = useSourceSpecificationLoad(
    sourceId
  );
  const onDropDownSelect = (sourceId: string) => {
    setSourceId(sourceId);
    const connector = dropDownData.find(item => item.value === sourceId);

    AnalyticsService.track("New Source - Action", {
      user_id: config.ui.workspaceId,
      action: "Select a connector",
      connector_source: connector?.text,
      connector_source_id: sourceId
    });
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
    <>
      <ConnectionBlock itemTo={{ name: destination.name }} />
      <ContentCard title={<FormattedMessage id="onboarding.sourceSetUp" />}>
        <ServiceForm
          onDropDownSelect={onDropDownSelect}
          onSubmit={onSubmitForm}
          formType="source"
          dropDownData={dropDownData}
          specifications={sourceSpecification?.connectionSpecification}
          hasSuccess={hasSuccess}
          errorMessage={errorMessage}
          isLoading={isLoading}
        />
      </ContentCard>
    </>
  );
};

export default CreateSourcePage;
