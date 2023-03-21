import React, { useState } from "react";

import { Link } from "components";
import { GlobIcon } from "components/icons/GlobIcon";

import { LOCALES } from "locales";

import styles from "./FormHeaderSection.module.scss";

interface Iporps {
  text: string;
  link: string;
  buttonText: string;
}

export const FormHeaderSection: React.FC<Iporps> = ({ text, link, buttonText }) => {
  const [language] = useState<string>(LOCALES.ENGLISH); // setLanguage

  return (
    <div className={styles.head}>
      <div className={styles.selectBox}>
        <div className={styles.globalIcon}>
          <GlobIcon color="#374151" />
        </div>
        <select
          name={language}
          className={styles.select}
          onChange={(event) => {
            console.log(event.target.value);
            // setLanguage(() => {
            //   return option.value;
            // });
          }}
        >
          <option value={LOCALES.ENGLISH}>English</option>
          <option value={LOCALES.CHINESE_SIMPLIFIED}>简体中文</option>
        </select>
      </div>
      <div className={styles.headRight}>
        <div className={styles.headRightText}>{text}</div>
        <button className={styles.button}>
          <Link $clear to={link}>
            {buttonText}
          </Link>
        </button>
      </div>
    </div>
  );
};
