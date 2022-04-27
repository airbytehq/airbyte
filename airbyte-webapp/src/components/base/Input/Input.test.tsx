import { render } from "@testing-library/react";

import { Input } from "./Input";

describe("<Input />", () => {
  test("renders text input", () => {
    const value = "aribyte@example.com";
    const { getByTestId, queryByTestId } = render(<Input type="text" defaultValue={value} />);

    expect(getByTestId("input")).toHaveAttribute("type", "text");
    expect(getByTestId("input")).toHaveValue(value);
    expect(queryByTestId("toggle-password-visibility-button")).toBeFalsy();
  });

  test("renders other type of input", () => {
    const type = "number";
    const value = 888;
    const { getByTestId, queryByTestId } = render(<Input type={type} defaultValue={value} />);

    expect(getByTestId("input")).toHaveAttribute("type", type);
    expect(getByTestId("input")).toHaveValue(value);
    expect(queryByTestId("toggle-password-visibility-button")).toBeFalsy();
  });

  test("renders password input with visibilty button", () => {
    const value = "eight888";
    const { getByTestId, getByRole } = render(<Input type="password" defaultValue={value} />);

    expect(getByTestId("input")).toHaveAttribute("type", "password");
    expect(getByTestId("input")).toHaveValue(value);
    expect(getByRole("img", { hidden: true })).toHaveAttribute("data-icon", "eye");
  });

  test("renders visible password when visibility button is clicked", () => {
    const value = "eight888";
    const { getByTestId, getByRole } = render(<Input type="password" defaultValue={value} />);

    getByTestId("toggle-password-visibility-button").click();

    expect(getByTestId("input")).toHaveAttribute("type", "text");
    expect(getByTestId("input")).toHaveValue(value);
    expect(getByRole("img", { hidden: true })).toHaveAttribute("data-icon", "eye-slash");
  });
});
