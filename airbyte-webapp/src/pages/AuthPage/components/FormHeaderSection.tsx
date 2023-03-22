import React, { useState } from "react";

import { DropDownRow, Link } from "components";

import { useUser } from "core/AuthContext";
import { LOCALES } from "locales";
import { LanguageDropdown } from "pages/SettingsPage/pages/AccountSettingsPage/pages/LanguagePage/components/LanguageDropdown";

import styles from "./FormHeaderSection.module.scss";

interface Iporps {
  text: string;
  link: string;
  buttonText: string;
}

export const FormHeaderSection: React.FC<Iporps> = ({ text, link, buttonText }) => {
  const { user, updateUserLang } = useUser();
  const { lang } = user;

  const [language, setLanguage] = useState<string>(lang ? lang : LOCALES.ENGLISH);

  const onUpdateLang = (option: DropDownRow.IDataItem) => {
    setLanguage(option.value);
    updateUserLang?.(option.value);
  };

  return (
    <div className={styles.head}>
      <div className={styles.selectBox}>
        <LanguageDropdown value={language} onChange={(option) => onUpdateLang(option)} />
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
