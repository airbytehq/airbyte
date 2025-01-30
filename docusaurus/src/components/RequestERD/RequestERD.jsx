import { useLocation } from "@docusaurus/router";
import React, { useEffect, useState } from "react";
import { EmailModal } from "./EmailModal";
import styles from "./RequestERD.module.css";
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
const { getRegistryEntry } = require("../../remark/utils");
const { getFromPaths } = require("../../helpers/objects");

export const RequestERD = () => {
  const location = useLocation();
  const [hasERD, setHasERD] = useState(false);
  const [source, setSource] = useState(null);

  const [isModalOpen, setIsModalOpen] = useState(false);

  const isSourcePage = /\/sources\/[^/]+/.test(location.pathname);

  useEffect(() => {
    async function checkExistingERD() {
      const entry = await getRegistryEntry({ path: location.pathname });
      const erdUrl = getFromPaths(entry, "erdUrl_[oss|cloud]");
      setHasERD(Boolean(erdUrl));
      const name = getFromPaths(entry, "name_[oss|cloud]");
      setSource({
        name,
        definitionId: entry.definitionId,
      });
    }

    if (isSourcePage) {
      checkExistingERD();
    }
  }, [location.pathname]);

  const handleRequestERD = () => {
    setIsModalOpen(true);
  };

  if (!isSourcePage || hasERD) {
    return null;
  }

  return (
    <>
      <div className={styles.requestERD}>
        <button className={styles.requestERDButton} onClick={handleRequestERD}>
          <FontAwesomeIcon icon={faPlus} />
          Request Entity-Relationship Diagram
        </button>
      </div>
      <EmailModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        sourceInfo={{
          url: location.pathname,
          name: source?.name,
          definitionId: source?.definitionId,
        }}
      />
    </>
  );
};
