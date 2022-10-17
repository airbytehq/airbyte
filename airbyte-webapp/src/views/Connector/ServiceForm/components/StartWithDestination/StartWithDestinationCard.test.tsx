import { fireEvent, render, waitFor } from "@testing-library/react";
import { IntlProvider } from "react-intl";

import en from "locales/en.json";

import { mockData } from "../../../../../test-utils/mock-data/mockStartWithDestination";
import { StartWithDestinationCard, StartWithDestinationProps } from "./StartWithDestinationCard";

const renderStartWithDestination = (props: StartWithDestinationProps) =>
  render(
    <IntlProvider locale="en" messages={en}>
      <StartWithDestinationCard {...props} />
    </IntlProvider>
  );

describe("<StartWithDestinationCard />", () => {
  it("should renders without crash with provided props", () => {
    const component = renderStartWithDestination({ destination: mockData, onDestinationSelect: jest.fn() });

    expect(component).toMatchSnapshot();
  });

  it("should call provided handler with right params", async () => {
    const handler = jest.fn();
    const { getByText } = renderStartWithDestination({ destination: mockData, onDestinationSelect: handler });

    fireEvent.click(getByText("Start with MongoDB"));
    await waitFor(() => {
      expect(handler).toHaveBeenCalledTimes(1);
      expect(handler).toHaveBeenCalledWith("8b746512-8c2e-6ac1-4adc-b59faafd473c");
    });
  });
});
