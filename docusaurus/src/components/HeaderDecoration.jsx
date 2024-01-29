import React from "react";
import styles from "./HeaderDecoration.module.css";

const capitalizeFirstLetter = (string) => {
  return string.charAt(0).toUpperCase() + string.slice(1);
};

const CHECK_ICON = (
  <svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 512 512">
    <title>Available</title>
    <path
      fill="currentColor"
      d="M256 48a208 208 0 1 1 0 416 208 208 0 1 1 0-416zm0 464A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM369 209c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-111 111-47-47c-9.4-9.4-24.6-9.4-33.9 0s-9.4 24.6 0 33.9l64 64c9.4 9.4 24.6 9.4 33.9 0L369 209z"
    />
  </svg>
);
const CROSS_ICON = (
  <svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 512 512">
    <title>Not available</title>
    <path
      fill="currentColor"
      d="M256 48a208 208 0 1 1 0 416 208 208 0 1 1 0-416zm0 464A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM175 175c-9.4 9.4-9.4 24.6 0 33.9l47 47-47 47c-9.4 9.4-9.4 24.6 0 33.9s24.6 9.4 33.9 0l47-47 47 47c9.4 9.4 24.6 9.4 33.9 0s9.4-24.6 0-33.9l-47-47 47-47c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-47 47-47-47c-9.4-9.4-24.6-9.4-33.9 0z"
    />
  </svg>
);

export const HeaderDecoration = ({
  isOss: isOssString,
  isCloud: isCloudString,
  isPypiPublished: isPypiPublishedString,
  dockerImageTag,
  supportLevel,
  iconUrl,
  originalTitle,
  originalId,
  github_url,
}) => {
  const isOss = isOssString.toUpperCase() === "TRUE";
  const isCloud = isCloudString.toUpperCase() === "TRUE";
  const isPypiPublished = isPypiPublishedString.toUpperCase() === "TRUE";

  return (
    <>
      <dl className={styles.connectorMetadata}>
        <div>
          <dt>Availability</dt>
          <dd className={styles.availability}>
            <span className={isCloud ? styles.available : styles.unavailable}>
              {isCloud ? CHECK_ICON : CROSS_ICON} Airbyte Cloud
            </span>
            <span className={isOss ? styles.available : styles.unavailable}>
              {isOss ? CHECK_ICON : CROSS_ICON} Airbyte OSS
            </span>
            {isPypiPublished && <a href="#usage-with-airbyte-lib" className={styles.available}>{CHECK_ICON} airbyte_lib</a>}
          </dd>
        </div>
        <div>
          <dt>Support Level</dt>
          <dd>
            <a href="/project-overview/product-support-levels/">
              {capitalizeFirstLetter(supportLevel)}
            </a>
          </dd>
        </div>
        <div>
          <dt>Latest Version</dt>
          <dd>
            <a href={github_url} target="_blank">
              {dockerImageTag}
            </a>
          </dd>
        </div>
      </dl>

      <div className={styles.header}>
        <img src={iconUrl} alt="" className={styles.connectorIcon} />
        <h1 id={originalId}>{originalTitle}</h1>
      </div>
    </>
  );
};

