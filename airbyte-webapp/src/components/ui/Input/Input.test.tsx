import { fireEvent, waitFor } from "@testing-library/react";
import { act } from "react-dom/test-utils";
import { render } from "test-utils/testutils";

import { Input } from "./Input";
// eslint-disable-next-line css-modules/no-unused-class
import styles from "./Input.module.scss";

describe("<Input />", () => {
  it("renders text input", async () => {
    const value = "aribyte@example.com";
    const { getByTestId, queryByTestId } = await render(<Input type="text" defaultValue={value} />);

    expect(getByTestId("input")).toHaveAttribute("type", "text");
    expect(getByTestId("input")).toHaveValue(value);
    expect(queryByTestId("toggle-password-visibility-button")).toBeFalsy();
  });

  it("renders another type of input", async () => {
    const type = "number";
    const value = 888;
    const { getByTestId, queryByTestId } = await render(<Input type={type} defaultValue={value} />);

    expect(getByTestId("input")).toHaveAttribute("type", type);
    expect(getByTestId("input")).toHaveValue(value);
    expect(queryByTestId("toggle-password-visibility-button")).toBeFalsy();
  });

  it("renders password input with visibilty button", async () => {
    const value = "eight888";
    const { getByTestId, getByRole } = await render(<Input type="password" defaultValue={value} />);

    expect(getByTestId("input")).toHaveAttribute("type", "password");
    expect(getByTestId("input")).toHaveValue(value);
    expect(getByRole("img", { hidden: true })).toHaveAttribute("data-icon", "eye");
  });

  it("renders visible password when visibility button is clicked", async () => {
    const value = "eight888";
    const { getByTestId, getByRole } = await render(<Input type="password" defaultValue={value} />);

    getByTestId("toggle-password-visibility-button")?.click();

    const inputEl = getByTestId("input") as HTMLInputElement;

    expect(inputEl).toHaveAttribute("type", "text");
    expect(inputEl).toHaveValue(value);
    expect(inputEl.selectionStart).toBe(value.length);
    expect(getByRole("img", { hidden: true })).toHaveAttribute("data-icon", "eye-slash");
  });

  it("showing password should remember cursor position", async () => {
    const value = "eight888";
    const selectionStart = Math.round(value.length / 2);

    const { getByTestId } = await render(<Input type="password" defaultValue={value} />);
    const inputEl = getByTestId("input") as HTMLInputElement;

    act(() => {
      inputEl.selectionStart = selectionStart;
    });

    getByTestId("toggle-password-visibility-button")?.click();

    expect(inputEl.selectionStart).toBe(selectionStart);
  });

  it("hides password on blur", async () => {
    const value = "eight888";
    const { getByTestId, getByRole } = await render(<Input type="password" defaultValue={value} />);

    getByTestId("toggle-password-visibility-button").click();

    const inputEl = getByTestId("input");

    expect(inputEl).toHaveFocus();
    act(() => inputEl.blur());

    await waitFor(() => {
      expect(inputEl).toHaveAttribute("type", "password");
      expect(getByRole("img", { hidden: true })).toHaveAttribute("data-icon", "eye");
    });
  });

  it("cursor position should be at the end after blur and and clicking on show password button", async () => {
    const value = "eight888";
    const { getByTestId } = await render(<Input type="password" defaultValue={value} />);
    const inputEl = getByTestId("input") as HTMLInputElement;

    getByTestId("toggle-password-visibility-button").click();
    expect(inputEl).toHaveFocus();
    act(() => {
      inputEl.selectionStart = value.length / 2;
      inputEl.blur();
    });

    await waitFor(() => {
      expect(inputEl).toHaveAttribute("type", "password");
    });

    getByTestId("toggle-password-visibility-button").click();
    expect(inputEl).toHaveFocus();
    expect(inputEl.selectionStart).toBe(value.length);
  });

  it("should trigger onChange once", async () => {
    const onChange = jest.fn();
    const { getByTestId } = await render(<Input onChange={onChange} />);
    const inputEl = getByTestId("input");

    fireEvent.change(inputEl, { target: { value: "one more test" } });
    expect(onChange).toHaveBeenCalledTimes(1);
  });

  it("has focused class after focus", async () => {
    const { getByTestId } = await render(<Input />);
    const inputEl = getByTestId("input");

    fireEvent.focus(inputEl);
    fireEvent.focus(inputEl);

    expect(getByTestId("input-container")).toHaveClass(styles.focused);
  });

  it("does not have focused class after blur", async () => {
    const { getByTestId } = await render(<Input />);
    const inputEl = getByTestId("input");

    fireEvent.focus(inputEl);
    fireEvent.blur(inputEl);
    fireEvent.blur(inputEl);

    expect(getByTestId("input-container")).not.toHaveClass(styles.focused);
  });

  it("calls onFocus if passed as prop", async () => {
    const onFocus = jest.fn();
    const { getByTestId } = await render(<Input onFocus={onFocus} />);
    const inputEl = getByTestId("input");

    fireEvent.focus(inputEl);

    expect(onFocus).toHaveBeenCalledTimes(1);
  });

  it("calls onBlur if passed as prop", async () => {
    const onBlur = jest.fn();
    const { getByTestId } = await render(<Input onBlur={onBlur} />);
    const inputEl = getByTestId("input");

    fireEvent.blur(inputEl);

    expect(onBlur).toHaveBeenCalledTimes(1);
  });
});
