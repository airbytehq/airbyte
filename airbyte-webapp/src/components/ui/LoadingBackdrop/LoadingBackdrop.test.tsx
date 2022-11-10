import { render } from "@testing-library/react";

import { LoadingBackdrop } from "./LoadingBackdrop";

describe("<LoadingBackdrop />", () => {
  it("loading backdrop is active", () => {
    const { getByTestId } = render(<LoadingBackdrop loading />);

    expect(getByTestId("loading-backdrop")).toBeInTheDocument();
  });

  it("loading backdrop is not active", () => {
    const { queryByTestId } = render(<LoadingBackdrop loading={false} />);

    expect(queryByTestId("loading-backdrop")).toBeNull();
  });
});
