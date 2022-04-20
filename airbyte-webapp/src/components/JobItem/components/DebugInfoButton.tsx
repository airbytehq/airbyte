import { faFileAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useState } from "react";
import { useIntl } from "react-intl";

import { Button } from "components";

import { JobDebugRead } from "../../../core/request/GeneratedApi";
import DebugInfoDetailsModal from "./DebugInfoDetailsModal";

type IProps = {
  jobDebugInfo: JobDebugRead;
};

const DebugInfoButton: React.FC<IProps> = ({ jobDebugInfo }) => {
  const { formatMessage } = useIntl();
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <Button
        onClick={() => setIsModalOpen(true)}
        secondary
        title={formatMessage({
          id: "sources.debugInfoDetails",
        })}
      >
        <FontAwesomeIcon icon={faFileAlt} />
      </Button>
      {isModalOpen && <DebugInfoDetailsModal jobDebugInfo={jobDebugInfo} onClose={() => setIsModalOpen(false)} />}
    </>
  );
};

export default DebugInfoButton;
