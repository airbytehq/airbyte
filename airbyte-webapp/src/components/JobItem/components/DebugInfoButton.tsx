import React, { useState } from "react";
import { useIntl } from "react-intl";
import styled from "styled-components";

import DebugInfoDetailsModal from "./DebugInfoDetailsModal";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faFileAlt } from "@fortawesome/free-solid-svg-icons";

import { Button } from "components";

import { JobDebugInfoMeta } from "core/domain/job";

const DebugInfo = styled(Button)`
  position: absolute;
  top: 9px;
  right: 64px;
`;

type IProps = {
  jobDebugInfo: JobDebugInfoMeta;
};

const DebugInfoButton: React.FC<IProps> = ({ jobDebugInfo }) => {
  const formatMessage = useIntl().formatMessage;
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <DebugInfo
        onClick={() => setIsModalOpen(true)}
        secondary
        title={formatMessage({
          id: "sources.debugInfoDetails",
        })}
      >
        <FontAwesomeIcon icon={faFileAlt} />
      </DebugInfo>
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
