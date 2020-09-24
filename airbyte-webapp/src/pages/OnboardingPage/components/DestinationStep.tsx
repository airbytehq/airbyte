import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useResource, useFetcher } from "rest-hooks";

import ContentCard from "../../../components/ContentCard";
import ServiceForm from "../../../components/ServiceForm";
import ConnectionBlock from "../../../components/ConnectionBlock";
import DestinationSpecificationResource, {
  DestinationSpecification
} from "../../../core/resources/DestinationSpecification";
import SourceResource from "../../../core/resources/Source";
import { AnalyticsService } from "../../../core/analytics/AnalyticsService";
import config from "../../../config";
import PrepareDropDownLists from "./PrepareDropDownLists";

type IProps = {
  dropDownData: Array<{ text: string; value: string; img?: string }>;
  hasSuccess?: boolean;
  onSubmit: (values: {
    name: string;
    serviceType: string;
    specificationId?: string;
    connectionConfiguration?: any;
  }) => void;
  errorStatus?: number;
  currentSourceId: string;
};

const useDestinationSpecificationLoad = (destinationId: string) => {
  const [
    destinationSpecification,
    setDestinationSpecification
  ] = useState<null | DestinationSpecification>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchSourceSpecification = useFetcher(
    DestinationSpecificationResource.detailShape(),
    true
  );

  useEffect(() => {
    (async () => {
      if (destinationId) {
        setIsLoading(true);
        setDestinationSpecification(
          await fetchSourceSpecification({ destinationId })
        );
        setIsLoading(false);
      }
    })();
  }, [fetchSourceSpecification, destinationId]);

  return { destinationSpecification, isLoading };
};

const DestinationStep: React.FC<IProps> = ({
  onSubmit,
  dropDownData,
  hasSuccess,
  errorStatus,
  currentSourceId
}) => {
  const [destinationId, setDestinationId] = useState("");
  const {
    destinationSpecification,
    isLoading
  } = useDestinationSpecificationLoad(destinationId);
  const currentSource = useResource(SourceResource.detailShape(), {
    sourceId: currentSourceId
  });
  const { getDestinationById } = PrepareDropDownLists();

  const onDropDownSelect = (sourceId: string) => {
    const destinationConnector = getDestinationById(sourceId);
    AnalyticsService.track("New Destination - Action", {
      user_id: config.ui.workspaceId,
      action: "Select a connector",
      connector_destination: destinationConnector?.name,
      connector_destination_id: destinationConnector?.destinationId
    });
    setDestinationId(sourceId);
  };
  const onSubmitForm = async (values: {
    name: string;
    serviceType: string;
  }) => {
    await onSubmit({
      ...values,
      specificationId: destinationSpecification?.destinationSpecificationId
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
      <ConnectionBlock itemFrom={{ name: currentSource.name }} />
      <ContentCard
        title={<FormattedMessage id="onboarding.destinationSetUp" />}
      >
        <ServiceForm
          onDropDownSelect={onDropDownSelect}
          onSubmit={onSubmitForm}
          hasSuccess={hasSuccess}
          formType="destination"
          dropDownData={dropDownData}
          errorMessage={errorMessage}
          specifications={destinationSpecification?.connectionSpecification}
          documentationUrl={destinationSpecification?.documentationUrl}
          isLoading={isLoading}
        />
      </ContentCard>
    </>
  );
};

export default DestinationStep;
