import React, { useEffect, useState } from "react";
import erdBG from "../../static/img/erd-bg-cta.jpg";
import styles from "./ErdDiagram.module.css";
const { getRegistryEntry } = require("../remark/utils");
const { getFromPaths } = require("../helpers/objects");

export const ErdDiagram = ({}) => {
  const [erdUrl, setErdUrl] = useState(null);

  useEffect(() => {
    async function getErdUrl() {
      const entry = await getRegistryEntry({ path: window.location.pathname });
      const url = getFromPaths(entry, "erdUrl_[oss|cloud]");
      setErdUrl(url);
    }

    getErdUrl();
  }, []);

  if (!erdUrl) return null;

  return (
    <div className={styles.erdDiagram}>
      <a href={erdUrl} target="_blank">
        <img src={erdBG} />
      </a>
    </div>
  );
};
