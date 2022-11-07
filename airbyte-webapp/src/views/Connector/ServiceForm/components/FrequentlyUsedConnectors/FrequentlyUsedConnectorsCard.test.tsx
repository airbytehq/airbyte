import { fireEvent, render, waitFor } from "@testing-library/react";
import { IntlProvider } from "react-intl";

import en from "locales/en.json";

import { mockData } from "../../../../../test-utils/mock-data/mockFrequentlyUsedConnectors";
import { FrequentlyUsedConnectorsCard, FrequentlyUsedConnectorsCardProps } from "./FrequentlyUsedConnectorsCard";

const renderFrequentlyUsedConnectorsComponent = (props: FrequentlyUsedConnectorsCardProps) =>
  render(
    <IntlProvider locale="en" messages={en}>
      <FrequentlyUsedConnectorsCard {...props} />
    </IntlProvider>
  );

describe("<FrequentlyUsedConnectors />", () => {
  it("should renders with mock data without crash", () => {
    const component = renderFrequentlyUsedConnectorsComponent({
      connectorType: "source",
      connectors: mockData,
      onClick: jest.fn(),
    });

    expect(component).toMatchSnapshot();
  });

  it("should call provided handler with right param", async () => {
    const handler = jest.fn();
    const { getByText } = renderFrequentlyUsedConnectorsComponent({
      connectorType: "source",
      connectors: mockData,
      onClick: handler,
    });
    fireEvent.click(getByText("BigQuery"));

    await waitFor(() => {
      expect(handler).toHaveBeenCalledTimes(1);
      expect(handler).toHaveBeenCalledWith("2", "BigQuery");
    });
  });
});
