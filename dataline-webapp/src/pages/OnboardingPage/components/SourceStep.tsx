import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useFetcher } from "rest-hooks";

import ContentCard from "../../../components/ContentCard";
import ServiceForm from "../../../components/ServiceForm";
import SourceSpecification from "../../../core/resources/SourceSpecification";

type IProps = {
  onSubmit: () => void;
  dropDownData: Array<{ text: string; value: string; img?: string }>;
  hasSuccess?: boolean;
};

const useSourceSpecificationLoad = (sourceId: string) => {
  const [sourceSpecification, setSourceSpecification] = useState(null);

  const fetchSourceSpecification = useFetcher(
    SourceSpecification.detailShape(),
    true
  );

  useEffect(() => {
    (async () => {
      if (sourceId) {
        setSourceSpecification(await fetchSourceSpecification({ sourceId }));
      }
    })();
  }, [fetchSourceSpecification, sourceId]);

  return sourceSpecification;
};

const SourceStep: React.FC<IProps> = ({
  onSubmit,
  dropDownData,
  hasSuccess
}) => {
  const [sourceId, setSourceId] = useState("");
  const spec = useSourceSpecificationLoad(sourceId);
  console.log(spec); // TODO: add spec fields to form

  const onDropDownSelect = (sourceId: string) => setSourceId(sourceId);

  return (
    <ContentCard title={<FormattedMessage id="onboarding.sourceSetUp" />}>
      <ServiceForm
        onDropDownSelect={onDropDownSelect}
        onSubmit={onSubmit}
        formType="source"
        dropDownData={dropDownData}
        hasSuccess={hasSuccess}
      />
    </ContentCard>
  );
};

export default SourceStep;
