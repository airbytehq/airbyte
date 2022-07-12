import { render } from "@testing-library/react";
import { IntlProvider } from "react-intl";

import en from "../../../../../../packages/cloud/locales/en.json";
import { PersonQuoteCover, PersonQuoteCoverProps } from "./PersonQuoteCover";

const renderPersonQuoteCover = (props?: PersonQuoteCoverProps) =>
  render(
    <IntlProvider locale="en" messages={en}>
      <PersonQuoteCover {...props} />
    </IntlProvider>
  );

describe("<PersonQuoteCover />", () => {
  test("should render with default props", () => {
    const { asFragment } = renderPersonQuoteCover();

    expect(asFragment()).toMatchSnapshot();
  });

  test("should render with default props and without background image", () => {
    const { asFragment } = renderPersonQuoteCover({
      backgroundImageStyle: {
        backgroundImage: "none",
      },
    });

    expect(asFragment()).toMatchSnapshot();
  });

  test("should render with overridden props", () => {
    const { asFragment } = renderPersonQuoteCover({
      overlayGradientStyle: {
        //  https://github.com/jsdom/cssstyle/issues/148
        //  snapshot testing doesn't parse linear-gradient so for testing purpose we just check applying inline style
        background: "blue",
      },
      backgroundImageStyle: {
        backgroundImage: "url(/image.png)",
      },
      quoteText: "This is test text",
      quoteTextStyle: { fontSize: "30px" },
      logoImageSrc: "/new-logo.svg",
      quoteAuthorFullNameStyle: { color: "black", fontSize: "40px" },
      quoteAuthorJobTitleStyle: { color: "red", fontSize: "50px" },
    });

    expect(asFragment()).toMatchSnapshot();
  });
});
