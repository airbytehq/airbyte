import React from "react";
import styles from "./AppliesTo.module.css";

const Icon = () => {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 576 512">
      {/* Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. */}
      <path fill="currentColor" d="M264.5 5.2c14.9-6.9 32.1-6.9 47 0l218.6 101c8.5 3.9 13.9 12.4 13.9 21.8s-5.4 17.9-13.9 21.8l-218.6 101c-14.9 6.9-32.1 6.9-47 0L45.9 149.8C37.4 145.8 32 137.3 32 128s5.4-17.9 13.9-21.8L264.5 5.2zM476.9 209.6l53.2 24.6c8.5 3.9 13.9 12.4 13.9 21.8s-5.4 17.9-13.9 21.8l-218.6 101c-14.9 6.9-32.1 6.9-47 0L45.9 277.8C37.4 273.8 32 265.3 32 256s5.4-17.9 13.9-21.8l53.2-24.6 152 70.2c23.4 10.8 50.4 10.8 73.8 0l152-70.2zm-152 198.2l152-70.2 53.2 24.6c8.5 3.9 13.9 12.4 13.9 21.8s-5.4 17.9-13.9 21.8l-218.6 101c-14.9 6.9-32.1 6.9-47 0L45.9 405.8C37.4 401.8 32 393.3 32 384s5.4-17.9 13.9-21.8l53.2-24.6 152 70.2c23.4 10.8 50.4 10.8 73.8 0z"/>
    </svg>
  );
}

const enumerate = (words) => {
  if (words.length === 1) {
    return words[0];
  }

  const notLastWord = words.slice(0, words.length - 1);
  return `${notLastWord.join(", ")} and ${words[words.length - 1]}`;
};

export const AppliesTo = (props) => {
  const { selfManagedEnterprise, cloud, oss } = props;
  if (!selfManagedEnterprise && !cloud && !oss) {
    throw new Error("Need to specify at least one 'AppliesTo' environment.");
  }
  const environments = [];
  if (cloud) {
    environments.push("Airbyte Cloud");
  }
  if (selfManagedEnterprise) {
    environments.push("Airbyte Enterprise");
  }
  if (oss) {
    environments.push("Open Source");
  }

  return <div className={styles.appliesTo}>
    <div className={styles.header}>
      <Icon /> 
      <span>{enumerate(environments)} only</span>
    </div>
    <div>
      The following documentation only applies to {enumerate(environments)}.
      {selfManagedEnterprise && <> If you're not an Airbyte Enterprise customer yet, <a href="https://airbyte.com/talk-to-sales" target="_blank">talk to us</a>.</>}
      {cloud && <> You can <a href="https://cloud.airbyte.com" target="_blank">try Airbyte Cloud</a> for free with our 14-day trial.</>}
    </div>
  </div>;
};