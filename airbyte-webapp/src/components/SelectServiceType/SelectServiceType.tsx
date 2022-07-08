import { useState } from "react";
import { useToggle } from "react-use";

import { ServiceTypeDropdown } from "components/ServiceTypeDropdown/ServiceTypeDropdown";

import RequestConnectorModal from "views/Connector/RequestConnectorModal";

import { ServiceTypeControlProps } from "../ServiceTypeDropdown/ServiceTypeDropdown";

const SelectServiceType: React.FC<Omit<ServiceTypeControlProps, "onOpenRequestConnectorModal">> = ({
  formType,
  ...restProps
}) => {
  const [isOpenRequestModal, toggleOpenRequestModal] = useToggle(false);
  const [initialRequestName, setInitialRequestName] = useState<string>();

  return (
    <>
      <ServiceTypeDropdown
        formType={formType}
        onOpenRequestConnectorModal={(name) => {
          setInitialRequestName(name);
          toggleOpenRequestModal();
        }}
        {...restProps}
      />
      {isOpenRequestModal && (
        <RequestConnectorModal
          connectorType="source"
          initialName={initialRequestName}
          onClose={toggleOpenRequestModal}
        />
      )}
    </>
  );
};

export { SelectServiceType };
