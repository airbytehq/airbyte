import React from "react";
import styles from "./AiAgentsHome.module.css";

export const HeroBanner = ({ tagline, subtitle, primaryCta, secondaryCta }) => {
  return (
    <div className={styles.heroBanner}>
      <h1 className={styles.heroTagline}>{tagline}</h1>
      <p className={styles.heroSubtitle}>{subtitle}</p>
      <div className={styles.heroCtas}>
        {primaryCta && (
          <a className={styles.heroPrimaryCta} href={primaryCta.href}>
            {primaryCta.label}
          </a>
        )}
        {secondaryCta && (
          <a className={styles.heroSecondaryCta} href={secondaryCta.href}>
            {secondaryCta.label}
          </a>
        )}
      </div>
    </div>
  );
};
