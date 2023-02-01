import { render } from "@testing-library/react";

import { StatusIcon, StatusIconStatus } from "./StatusIcon";

describe("<StatusIcon />", () => {
  it("renders with title and default icon", () => {
    const title = "Pulpo";
    const value = 888;

    const component = render(<StatusIcon title={title} value={value} />);

    expect(component.getByTitle(title)).toBeDefined();
    expect(component.getByRole("img")).toHaveAttribute("data-icon", "cross");
    expect(component.getByText(`${value}`)).toBeDefined();
  });

  const statusCases: Array<{ status: StatusIconStatus; icon: string }> = [
    { status: "success", icon: "check" },
    { status: "inactive", icon: "pause" },
    { status: "sleep", icon: "moon" },
    { status: "warning", icon: "triangle-exclamation" },
    { status: "loading", icon: "circle-loader" },
    { status: "error", icon: "cross" },
    { status: "cancelled", icon: "minus" },
  ];

  it.each(statusCases)("renders $status status", ({ status, icon }) => {
    const title = `Status is ${status}`;
    const value = 888;
    const props = {
      title,
      value,
      status,
    };

    const component = render(<StatusIcon {...props} />);

    expect(component.getByTitle(title)).toBeDefined();
    expect(component.getByRole("img")).toHaveAttribute("data-icon", icon);
    expect(component.getByText(`${value}`)).toBeDefined();
  });
});
