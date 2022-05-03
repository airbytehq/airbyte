import { render } from "utils/testutils";

import { Input } from "./Input";

describe("<Input />", () => {
  test("renders text input", async () => {
    const value = "aribyte@example.com";
    const { getByTestId, queryByTestId } = await render(<Input type="text" defaultValue={value} />);

    expect(getByTestId("input")).toHaveAttribute("type", "text");
    expect(getByTestId("input")).toHaveValue(value);
    expect(queryByTestId("toggle-password-visibility-button")).toBeFalsy();
  });

  test("renders another type of input", async () => {
    const type = "number";
    const value = 888;
    const { getByTestId, queryByTestId } = await render(<Input type={type} defaultValue={value} />);

    expect(getByTestId("input")).toHaveAttribute("type", type);
    expect(getByTestId("input")).toHaveValue(value);
    expect(queryByTestId("toggle-password-visibility-button")).toBeFalsy();
  });

  test("renders password input with visibilty button", async () => {
    const value = "eight888";
    const { getByTestId, getByRole } = await render(<Input type="password" defaultValue={value} />);

    expect(getByTestId("input")).toHaveAttribute("type", "password");
    expect(getByTestId("input")).toHaveValue(value);
    expect(getByRole("img", { hidden: true })).toHaveAttribute("data-icon", "eye");
  });

  test("renders visible password when visibility button is clicked", async () => {
    const value = "eight888";
    const { getByTestId, getByRole } = await render(<Input type="password" defaultValue={value} />);

    getByTestId("toggle-password-visibility-button")?.click();

    expect(getByTestId("input")).toHaveAttribute("type", "text");
    expect(getByTestId("input")).toHaveValue(value);
    expect(getByRole("img", { hidden: true })).toHaveAttribute("data-icon", "eye-slash");
  });
});
