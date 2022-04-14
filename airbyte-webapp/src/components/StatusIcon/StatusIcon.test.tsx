import { render } from "@testing-library/react";

import StatusIcon from "./StatusIcon";

describe("<StatusIcon />", () => {
  test("renders with title and default icon", () => {
    const title = "Pulpo";
    const value = 888;

    const component = render(<StatusIcon title={title} value={value} />);

    expect(component.getByTitle(title)).toBeDefined();
    expect(component.getByRole("img")).toHaveAttribute("data-icon", "times");
    expect(component.getByText(`${value}`)).toBeDefined();
  });

  const statusCases = [
    { status: "success", icon: "check" },
    { status: "inactive", icon: "pause" },
    { status: "empty", icon: "ban" },
    { status: "warning", icon: "exclamation-triangle" },
  ];

  test.each(statusCases)("renders $status status", ({ status, icon }) => {
    const title = `Status is ${status}`;
    const value = 888;
    const props = {
      title,
      value,
      [status]: true,
    };

    const component = render(<StatusIcon {...props} />);

    expect(component.getByTitle(title)).toBeDefined();
    expect(component.getByRole("img")).toHaveAttribute("data-icon", icon);
    expect(component.getByText(`${value}`)).toBeDefined();
  });
});
