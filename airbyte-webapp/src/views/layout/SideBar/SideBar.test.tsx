import { render, screen } from "@testing-library/react";
import { TestWrapper } from "test-utils/testutils";

import { SideBar } from "./SideBar";

describe("<SideBar/>", () => {
  it("renders the main nav items", () => {
    render(<SideBar />, { wrapper: TestWrapper });
    const navItems = screen.getByTestId("navMainItems").querySelectorAll("li");
    expect(navItems.length).toBe(3);
    expect(navItems[0]).toContainHTML('<a class="menuItem" data-testid="sourcesLink"');
    expect(navItems[1]).toContainHTML('<a class="menuItem" data-testid="destinationsLink"');
    expect(navItems[2]).toContainHTML('<a class="menuItem" data-testid="connectionsLink"');
  });
  it("renders with default bottomItems if none are passed in", () => {
    render(<SideBar />, { wrapper: TestWrapper });

    const listItems = screen.getByTestId("navBottomMenu").querySelectorAll("li");
    expect(listItems.length).toBe(4);
    expect(listItems[0]).toContainHTML('<a class="menuItem" data-testid="updateLink"');
    expect(listItems[3]).toContainHTML("dev"); // version "number"
  });
});
