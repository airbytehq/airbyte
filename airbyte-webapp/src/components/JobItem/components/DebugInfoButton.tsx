import React, { useState } from "react";
import { useIntl } from "react-intl";

import DebugInfoDetailsModal from "./DebugInfoDetailsModal";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faFileAlt } from "@fortawesome/free-solid-svg-icons";

import { Button } from "components";

import { JobDebugInfoMeta } from "core/domain/job";

type IProps = {
  jobDebugInfo: JobDebugInfoMeta;
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
      {isModalOpen && (
        <DebugInfoDetailsModal
          jobDebugInfo={jobDebugInfo}
          onClose={() => setIsModalOpen(false)}
        />
      )}
    </>
  );
};

export default DebugInfoButton;
