import type { IntlConfig } from "react-intl";

import React, { useContext, useMemo, useState } from "react";
import { IntlProvider } from "react-intl";

type Messages = IntlConfig["messages"];

interface I18nContext {
  setMessageOverwrite: (messages: Messages) => void;
}

const i18nContext = React.createContext<I18nContext>({ setMessageOverwrite: () => null });

export const useI18nContext = () => {
  return useContext(i18nContext);
};

interface I18nProviderProps {
  messages: Messages;
  locale: string;
}

export const I18nProvider: React.FC<React.PropsWithChildren<I18nProviderProps>> = ({ children, messages, locale }) => {
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
      ...messages,
      ...(overwrittenMessages ?? {}),
    }),
    [messages, overwrittenMessages]
  );

  return (
    <i18nContext.Provider value={i18nOverwriteContext}>
      <IntlProvider
        locale={locale}
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
