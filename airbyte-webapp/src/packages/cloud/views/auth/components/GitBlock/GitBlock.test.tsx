import { render } from "@testing-library/react";
import { IntlProvider } from "react-intl";

import { ConfigContext, defaultConfig } from "config";

import en from "../../../../locales/en.json";
import { GitBlock, GitBlockProps } from "./GitBlock";

const renderGitBlock = (props?: GitBlockProps) =>
  render(
    <IntlProvider locale="en" messages={en}>
      <ConfigContext.Provider value={{ config: defaultConfig }}>
        <GitBlock {...props} />
      </ConfigContext.Provider>
    </IntlProvider>
  );

describe("<GitBlock />", () => {
  test("should render with default props", () => {
    const { asFragment } = renderGitBlock();

    expect(asFragment()).toMatchSnapshot();
  });

  test("should render with overwritten props", () => {
    const { asFragment } = renderGitBlock({
      titleStyle: { fontSize: "30px" },
      messageStyle: { color: "blue" },
    });

    expect(asFragment()).toMatchSnapshot();
  });
});
