import { render } from "@testing-library/react";
import { act, renderHook } from "@testing-library/react-hooks";
import React from "react";
import { FormattedMessage, IntlConfig, useIntl } from "react-intl";

import { I18nProvider, useI18nContext } from "./I18nProvider";

const provider = (messages: IntlConfig["messages"], locale = "en"): React.FC<React.PropsWithChildren<unknown>> => {
  return ({ children }) => (
    <I18nProvider locale={locale} messages={messages}>
      {children}
    </I18nProvider>
  );
};

const useMessages = () => {
  const { setMessageOverwrite } = useI18nContext();
  const { messages } = useIntl();
  return { setMessageOverwrite, messages };
};

describe("I18nProvider", () => {
  it("should set the react-intl locale correctly", () => {
    const { result } = renderHook(() => useIntl(), {
      wrapper: provider({}, "fr"),
    });
    expect(result.current.locale).toBe("fr");
  });

  it("should set messages for consumption via react-intl", () => {
    const wrapper = render(
      <span data-testid="msg">
        <FormattedMessage id="test.id" />
      </span>,
      { wrapper: provider({ "test.id": "Hello world!" }) }
    );
    expect(wrapper.getByTestId("msg").textContent).toBe("Hello world!");
  });

  it("should allow render <b></b> tags for every message", () => {
    const wrapper = render(
      <span data-testid="msg">
        <FormattedMessage id="test.id" />
      </span>,
      { wrapper: provider({ "test.id": "Hello <b>world</b>!" }) }
    );
    expect(wrapper.getByTestId("msg").innerHTML).toBe("Hello <strong>world</strong>!");
  });

  describe("useI18nContext", () => {
    it("should allow overwriting default and setting additional messages", () => {
      const { result } = renderHook(() => useMessages(), {
        wrapper: provider({ test: "default message" }),
      });
      expect(result.current.messages).toHaveProperty("test", "default message");
      act(() => result.current.setMessageOverwrite({ test: "overwritten message", other: "new message" }));
      expect(result.current.messages).toHaveProperty("test", "overwritten message");
      expect(result.current.messages).toHaveProperty("other", "new message");
    });

    it("should allow resetting overwrites with an empty object", () => {
      const { result } = renderHook(() => useMessages(), {
        wrapper: provider({ test: "default message" }),
      });
      act(() => result.current.setMessageOverwrite({ test: "overwritten message" }));
      expect(result.current.messages).toHaveProperty("test", "overwritten message");
      act(() => result.current.setMessageOverwrite({}));
      expect(result.current.messages).toHaveProperty("test", "default message");
    });

    it("should allow resetting overwrites with undefined", () => {
      const { result } = renderHook(() => useMessages(), {
        wrapper: provider({ test: "default message" }),
      });
      act(() => result.current.setMessageOverwrite({ test: "overwritten message" }));
      expect(result.current.messages).toHaveProperty("test", "overwritten message");
      act(() => result.current.setMessageOverwrite(undefined));
      expect(result.current.messages).toHaveProperty("test", "default message");
    });
  });
});
