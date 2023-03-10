import type { IntlConfig } from "react-intl";

import React, { useContext, useMemo, useState } from "react";
import { IntlProvider } from "react-intl";

import { useUser } from "core/AuthContext";
import { LOCALES, messages } from "locales";

type Messages = IntlConfig["messages"];

interface I18nContext {
  setMessageOverwrite: (messages: Messages) => void;
}

const i18nContext = React.createContext<I18nContext>({ setMessageOverwrite: () => null });

export const useI18nContext = () => {
  return useContext(i18nContext);
};

interface I18nProviderProps {
  messages?: Messages;
  locale?: string;
}

export const I18nProvider: React.FC<I18nProviderProps> = ({ children }) => {
  const { lang } = useUser().user;

  const translatedMessages = messages[lang ? lang : LOCALES.ENGLISH];
  const [overwrittenMessages, setOvewrittenMessages] = useState<Messages>();

  const i18nOverwriteContext = useMemo<I18nContext>(
    () => ({
      setMessageOverwrite: (messages) => {
        setOvewrittenMessages(messages);
      },
    }),
    []
  );

  const mergedMessages = useMemo(
    () => ({
      ...translatedMessages,
      ...(overwrittenMessages ?? {}),
    }),
    [translatedMessages, overwrittenMessages]
  );

  return (
    <i18nContext.Provider value={i18nOverwriteContext}>
      <IntlProvider
        locale={lang}
        messages={mergedMessages}
        defaultRichTextElements={{
          b: (chunk) => <strong>{chunk}</strong>,
        }}
      >
        {children}
      </IntlProvider>
    </i18nContext.Provider>
  );
};
