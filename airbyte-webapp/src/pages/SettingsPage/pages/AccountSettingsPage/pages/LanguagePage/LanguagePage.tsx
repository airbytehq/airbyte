import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { LoadingButton } from "components";
import { Separator } from "components/Separator";

import { useUser } from "core/AuthContext";
import { useUserAsyncAction } from "services/users/UsersService";

import { LanguageDropdown } from "./components/LanguageDropdown";

const PageContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  padding: 30px 70px;
`;

const ChangeBtnContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
`;

const LanguagePage: React.FC = () => {
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
      <LanguageDropdown
        labelId="settings.language.dropdownLabel"
        value={language}
        onChange={(option) => {
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
