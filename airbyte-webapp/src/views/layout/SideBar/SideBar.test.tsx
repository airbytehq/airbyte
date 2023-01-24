import { render, screen } from "@testing-library/react";
import { TestWrapper } from "test-utils/testutils";

import { SideBar } from "./SideBar";

describe("<SideBar/>", () => {
  it("renders with default bottomItems if none are passed in", () => {
    render(<SideBar />, { wrapper: TestWrapper });

    const listItems = screen.getAllByRole("listitem");

    expect(listItems.length).toBe(2);
  });
});
