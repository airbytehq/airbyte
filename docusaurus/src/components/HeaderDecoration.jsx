import React from "react";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import styles from "./HeaderDecoration.module.css";
import { Chip } from "./Chip";
import { Callout } from "./Callout";

// Extend Day.js with the relativeTime plugin
dayjs.extend(relativeTime);

// ICONS

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

const SUCCESS_ICON = (
  <svg
    viewBox="0 0 16 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={styles.successIcon}
  >
    <g clip-path="url(#clip0_2157_7349)">
      <circle cx="8" cy="8" r="7.75" />
      <circle cx="8" cy="8" r="5.25" stroke-width="1.5" stroke="currentColor" />
      <path
        d="M5.5 8L7 9.5L10 6.5"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke="currentColor"
      />
    </g>
    <defs>
      <clipPath id="clip0_2157_7349">
        <rect width="16" height="16" />
      </clipPath>
    </defs>
  </svg>
);

const USAGE_ICON = (
  <svg
    viewBox="0 0 15 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={styles.usageIcon}
  >
    <g clip-path="url(#clip0_2157_7378)">
      <path
        d="M8.60324 6.73291L7.62417 7.41477L6.6451 6.73291C6.25109 6.45851 6 6.00842 6 5.5C6 4.67157 6.67157 4 7.5 4C8.32843 4 9 4.67157 9 5.5C9 6.34482 8.76279 6.6218 8.60324 6.73291ZM6.22888 10.2374L7.62417 9.69316L9.01946 10.2374C9.20066 10.3081 9.62334 10.6587 9.99922 11.7588C10.1324 12.1486 10.2373 12.5709 10.316 13H4.74144C4.83317 12.6029 4.95107 12.2089 5.0952 11.84C5.52444 10.7416 5.99622 10.3281 6.22888 10.2374Z"
        stroke-width="4"
      />
      <path
        className={styles.iconBackground}
        d="M8.75 5.5C8.75 6.19036 8.19036 6.75 7.5 6.75C6.80964 6.75 6.25 6.19036 6.25 5.5C6.25 4.80964 6.80964 4.25 7.5 4.25C8.19036 4.25 8.75 4.80964 8.75 5.5ZM10.946 7.98782C11.4514 7.28873 11.75 6.42907 11.75 5.5C11.75 3.15279 9.84721 1.25 7.5 1.25C5.15279 1.25 3.25 3.15279 3.25 5.5C3.25 6.42907 3.54856 7.28873 4.05399 7.98782C2.22057 9.13637 1 11.175 1 13.5C1 14.3284 1.67157 15 2.5 15C3.32843 15 4 14.3284 4 13.5C4 11.567 5.567 10 7.5 10C9.433 10 11 11.567 11 13.5C11 14.3284 11.6716 15 12.5 15C13.3284 15 14 14.3284 14 13.5C14 11.175 12.7794 9.13638 10.946 7.98782Z"
        stroke-width="1.5"
        stroke-linecap="round"
      />
      <circle
        stroke="currentColor"
        cx="7.5"
        cy="5.5"
        r="2.75"
        stroke-width="1.5"
      />
      <path
        d="M12.5 13.5C12.5 10.7386 10.2614 8.5 7.5 8.5C4.73858 8.5 2.5 10.7386 2.5 13.5"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="butt"
      />
    </g>
    <defs>
      <clipPath id="clip0_2157_7378">
        <rect width="15" height="16" />
      </clipPath>
    </defs>
  </svg>
);

// HELPERS

/**
 * Convert a string to a boolean
 *
 * Why? Because MDX doesn't support passing boolean values properly.
 */
const boolStringToBool = (boolString) => {
  // if value is a boolean, return it
  if (typeof boolString === "boolean") return boolString;

  if (boolString?.toUpperCase() === "TRUE") return true;
  if (boolString?.toUpperCase() === "FALSE") return false;

  return null;
};

/**
 * Convert an Optional string of high, medium, low to a number of 0, 1, 2, 3
 */
const levelToIcon = (level) => {
  switch (level?.toLowerCase()) {
    case "high":
      return 3;
    case "medium":
      return 2;
    case "low":
      return 1;
    default:
      return 0; // Default case for undefined or any other input
  }
};

// COMPONENTS

const IconRow = ({ iconComponent, number }) => {
  const icons = Array.from({ length: number }, (_, index) => (
    <div
      key={index}
      className={styles.iconWrapper}
      style={{ zIndex: number - index }}
    >
      {iconComponent}
    </div>
  ));

  return <div className={styles.iconRow}>{icons}</div>;
};


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
          <Chip
            className={isPypiPublished ? styles.available : styles.unavailable}
          >
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
          {lastUpdated && (
            <span
              className={styles.deemphasizeText}
            >{`(Last updated ${dayjs(lastUpdated).fromNow()})`}</span>
          )}
        </MetadataStat>
      )}
      {cdkVersion && (
        <MetadataStat label="CDK Version">
          <a target="_blank" href={cdkVersionUrl}>
            {cdkVersion}
          </a>
          {isLatestCDK && (
            <span className={styles.deemphasizeText}>{"(Latest)"}</span>
          )}
        </MetadataStat>
      )}
      {syncSuccessRate && (
        <MetadataStat label="Sync Success Rate">
          <IconRow
            iconComponent={SUCCESS_ICON}
            number={levelToIcon(syncSuccessRate)}
          />
        </MetadataStat>
      )}
      {usageRate && (
        <MetadataStat label="Usage Rate">
          <IconRow iconComponent={USAGE_ICON} number={levelToIcon(usageRate)} />
        </MetadataStat>
      )}
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
