import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";

import ContentCard from "../../../components/ContentCard";
import ServiceForm from "../../../components/ServiceForm";
import ConnectionBlock from "../../../components/ConnectionBlock";
import DestinationSpecificationResource, {
  DestinationSpecification
} from "../../../core/resources/DestinationSpecification";
import { useFetcher } from "rest-hooks";

type IProps = {
  hasSuccess?: boolean;
  onSubmit: (values: {
    name: string;
    serviceType: string;
    specificationId?: string;
    connectionConfiguration?: any;
  }) => void;
  dropDownData: Array<{ text: string; value: string; img?: string }>;
  errorMessage?: React.ReactNode;
};

const useDestinationSpecificationLoad = (destinationId: string) => {
  const [
    destinationSpecification,
    setDestinationSpecification
  ] = useState<null | DestinationSpecification>(null);

  const fetchSourceSpecification = useFetcher(
    DestinationSpecificationResource.detailShape(),
    true
  );

  useEffect(() => {
    (async () => {
      if (destinationId) {
        setDestinationSpecification(
          await fetchSourceSpecification({ destinationId })
        );
      }
    })();
  }, [fetchSourceSpecification, destinationId]);

  return destinationSpecification;
};

const Destination: React.FC<IProps> = ({
  onSubmit,
  dropDownData,
  hasSuccess,
  errorMessage
}) => {
  const [destinationId, setDestinationId] = useState("");
  const specification = useDestinationSpecificationLoad(destinationId);

  const onDropDownSelect = (sourceId: string) => setDestinationId(sourceId);
  const onSubmitForm = async (values: {
    name: string;
    serviceType: string;
  }) => {
    await onSubmit({
      ...values,
      specificationId: specification?.destinationSpecificationId
    });
  };

  return (
    <>
      <ConnectionBlock itemFrom={{ name: "Test 1" }} />
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
          specifications={specification?.connectionSpecification}
        />
      </ContentCard>
    </>
  );
};

export default Destination;
