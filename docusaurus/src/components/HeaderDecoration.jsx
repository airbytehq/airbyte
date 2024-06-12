import React from "react";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import styles from "./HeaderDecoration.module.css";
import { Chip } from "./Chip";
import { Callout } from "./Callout";

// Extend Day.js with the relativeTime plugin
dayjs.extend(relativeTime);

/**
 * Convert a string to a boolean
 *
 * Why? Because MDX doesn't support passing boolean values properly.
 */
const boolStringToBool = (boolString) => {
  // if value is a boolean, return it
  if (typeof boolString === "boolean") return boolString;

  if (boolString?.toUpperCase() === "TRUE") return true;
  if (boolString?.toUpperCase === "FALSE") return false;

  return null;
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


const MetadataStat = ({ label, children }) => (
  <div className={styles.metadataStat}>
    <dt className={styles.metadataStatLabel}>{`${label}: `}</dt>
    <dd className={styles.metadataStatValue}>{children}</dd>
  </div>
);

const EnabledIcon = ({ isEnabled }) => {
  return isEnabled ? CHECK_ICON : CROSS_ICON;
};

const ConnectorMetadataCallout = ({
  isCloud,
  isOss,
  isPypiPublished,
  supportLevel,
  github_url,
  dockerImageTag,
  cdkVersion,
  isLatestCDK,
  cdkVersionUrl,
  syncSuccessRate,
  usageRate,
  lastUpdated,
}) => (
  <Callout className={styles.connectorMetadataCallout}>
    <dl className={styles.connectorMetadata}>
      <MetadataStat label="Availability">
        <div className={styles.availability}>
          <Chip className={isCloud ? styles.available : styles.unavailable}>
            <EnabledIcon isEnabled={isCloud} /> Airbyte Cloud
          </Chip>
          <Chip className={isOss ? styles.available : styles.unavailable}>
            <EnabledIcon isEnabled={isOss} /> Airbyte OSS
          </Chip>
          <Chip className={isPypiPublished ? styles.available : styles.unavailable}>
            <EnabledIcon isEnabled={isPypiPublished} /> PyAirbyte
          </Chip>
        </div>
      </MetadataStat>
      <MetadataStat label="Support Level">
        <a href="/integrations/connector-support-levels/">
          <Chip>{supportLevel}</Chip>
        </a>
      </MetadataStat>
      {supportLevel !== "archived" && (
        <MetadataStat label="Connector Version">
          <a href={github_url} target="_blank">
            {dockerImageTag}
          </a>
          {lastUpdated && <span className={styles.deemphasizeText}>{`(Last updated ${dayjs(lastUpdated).fromNow()})`}</span>}
        </MetadataStat>
      )}
      {
        cdkVersion && (
          <MetadataStat label="CDK Version">
            <a target="_blank" href={cdkVersionUrl}>
              {cdkVersion}
            </a>
            {isLatestCDK && <span className={styles.deemphasizeText}>{"(Latest)"}</span>}
          </MetadataStat>
        )
      }
      {
        syncSuccessRate && (
          <MetadataStat label="Sync Success Rate">
            <Chip>{syncSuccessRate}</Chip>
          </MetadataStat>
        )
      }
      {
        usageRate && (
          <MetadataStat label="Usage Rate">
            <Chip>{usageRate}</Chip>
          </MetadataStat>
        )
      }
    </dl>
  </Callout>
);

const ConnectorTitle = ({ iconUrl, originalTitle, originalId, isArchived }) => (
  <div className={styles.header}>
    <img src={iconUrl} alt="" className={styles.connectorIcon} />
    <h1 id={originalId}>
      {isArchived ? (
        <span>
          {originalTitle} <span style={{ color: "gray" }}>[ARCHIVED]</span>
        </span>
      ) : (
        originalTitle
      )}
    </h1>
  </div>
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
  cdkVersion,
  isLatestCDKString,
  cdkVersionUrl,
  syncSuccessRate,
  usageRate,
  lastUpdated,
}) => {
  const isOss = boolStringToBool(isOssString);
  const isCloud = boolStringToBool(isCloudString);
  const isPypiPublished = boolStringToBool(isPypiPublishedString);
  const isLatestCDK = boolStringToBool(isLatestCDKString);
  const isArchived = supportLevel?.toUpperCase() === "ARCHIVED";


  return (
    <>
      <ConnectorTitle
        iconUrl={iconUrl}
        originalTitle={originalTitle}
        originalId={originalId}
        isArchived={isArchived}
      />
      <ConnectorMetadataCallout
        isCloud={isCloud}
        isOss={isOss}
        isPypiPublished={isPypiPublished}
        supportLevel={supportLevel}
        github_url={github_url}
        dockerImageTag={dockerImageTag}
        cdkVersion={cdkVersion}
        cdkVersionUrl={cdkVersionUrl}
        isLatestCDK={isLatestCDK}
        syncSuccessRate={syncSuccessRate}
        usageRate={usageRate}
        lastUpdated={lastUpdated}
      />
    </>
  );
};
