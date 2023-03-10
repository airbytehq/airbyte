import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import { DropDown, LoadingButton, DropDownRow } from "components";
import { Separator } from "components/Separator";

import { useUser } from "core/AuthContext";
import { LOCALES } from "locales";
import { useUserAsyncAction } from "services/users/UsersService";

const PageContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
`;

const DDLabel = styled.div`
  font-style: normal;
  font-weight: 500;
  font-size: 13px;
  line-height: 20px;
  color: #374151;
`;

const ChangeBtnContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
`;

const LanguagePage: React.FC = () => {
  const { formatMessage } = useIntl();
  const languages: DropDownRow.IDataItem[] = [
    { label: formatMessage({ id: "English" }), value: LOCALES.ENGLISH },
    { label: formatMessage({ id: "简体中文" }), value: LOCALES.CHINESE_SIMPLIFIED },
  ];

  const { user, updateUserLang } = useUser();
  const { onUpdateLang } = useUserAsyncAction();

  const [language, setLanguage] = useState<string>(user.lang);
  const [isUpdated, setIsUpdated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const updateLang = () => {
    setIsLoading(true);
    onUpdateLang(language)
      .then(() => {
        setIsUpdated(false);
        setIsLoading(false);
        updateUserLang?.(language);
      })
      .catch(() => {
        setIsUpdated(false);
        setIsLoading(false);
      });
  };

  return (
    <PageContainer>
      <DDLabel>
        <FormattedMessage id="settings.language.dropdownLabel" />
      </DDLabel>
      <DropDown
        $withBorder
        $background="white"
        options={languages}
        value={language}
        onChange={(option: DropDownRow.IDataItem) => {
          setLanguage((prevState) => {
            if (prevState !== option.value) {
              setIsUpdated(true);
            }
            return option.value;
          });
        }}
      />
      <Separator height="60px" />
      <ChangeBtnContainer>
        <LoadingButton size="lg" disabled={!isUpdated} isLoading={isLoading} onClick={updateLang}>
          <FormattedMessage id="settings.language.btnText" />
        </LoadingButton>
      </ChangeBtnContainer>
    </PageContainer>
  );
};

export default LanguagePage;
