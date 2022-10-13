import { render } from "@testing-library/react";

import Spinner from "./Spinner";

describe("<Spinner />", () => {
  it("should render without crash", () => {
    const { asFragment } = render(<Spinner />);

    expect(asFragment()).toMatchSnapshot();
  });
});
