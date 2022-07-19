import { fireEvent } from "@testing-library/react";

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

  test("should trigger onChange once", async () => {
    const onChange = jest.fn();
    const { getByTestId } = await render(<Input onChange={onChange} />);
    const inputEl = getByTestId("input");

    fireEvent.change(inputEl, { target: { value: "one more test" } });
    expect(onChange).toHaveBeenCalledTimes(1);
  });

  test("has focused class after focus", async () => {
    const { getByTestId } = await render(<Input />);
    const inputEl = getByTestId("input");

    fireEvent.focus(inputEl);
    fireEvent.focus(inputEl);

    expect(getByTestId("input-container")).toHaveClass("input-container--focused");
  });

  test("does not have focused class after blur", async () => {
    const { getByTestId } = await render(<Input />);
    const inputEl = getByTestId("input");

    fireEvent.focus(inputEl);
    fireEvent.blur(inputEl);
    fireEvent.blur(inputEl);

    expect(getByTestId("input-container")).not.toHaveClass("input-container--focused");
  });

  test("calls onFocus if passed as prop", async () => {
    const onFocus = jest.fn();
    const { getByTestId } = await render(<Input onFocus={onFocus} />);
    const inputEl = getByTestId("input");

    fireEvent.focus(inputEl);

    expect(onFocus).toHaveBeenCalledTimes(1);
  });

  test("calls onBlur if passed as prop", async () => {
    const onBlur = jest.fn();
    const { getByTestId } = await render(<Input onBlur={onBlur} />);
    const inputEl = getByTestId("input");

    fireEvent.blur(inputEl);

    expect(onBlur).toHaveBeenCalledTimes(1);
  });
});
