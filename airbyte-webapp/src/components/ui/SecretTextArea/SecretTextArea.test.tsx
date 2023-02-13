import userEvent from "@testing-library/user-event";
import { act } from "react-dom/test-utils";
import { render } from "test-utils/testutils";

import { SecretTextArea } from "./SecretTextArea";

// eslint-disable-next-line @typescript-eslint/no-empty-function
const emptyFn = () => {};

describe("SecretTextArea", () => {
  it("renders textarea when there is no initial value", async () => {
    const { queryByTestId, container } = await render(<SecretTextArea />);

    expect(container.querySelector("textarea")).toBeInTheDocument();
    expect(queryByTestId("secret-text-area-visibility-button")).not.toBeInTheDocument();
    expect(container.querySelector('input[type="password"]')).not.toBeInTheDocument();
  });

  it("renders on hidden input when there is an initial value", async () => {
    const value = "Here is my secret text";
    const { getByTestId, queryByTestId, container } = await render(<SecretTextArea value={value} onChange={emptyFn} />);

    expect(container.querySelector("textarea")).not.toBeInTheDocument();
    expect(queryByTestId("secret-text-area-visibility-button")).toBeInTheDocument();

    const input = getByTestId("secret-text-area-input");
    expect(input).toHaveAttribute("type", "password");
    expect(input).toHaveAttribute("aria-hidden");
    expect(input).toHaveValue(value);
  });

  it("renders disabled when disabled is set", async () => {
    const { getByTestId } = await render(<SecretTextArea disabled />);

    expect(getByTestId("text-input-container")).toHaveClass("disabled");
    expect(getByTestId("secret-text-area-text-area")).toBeDisabled();
  });

  it("renders disabled when disabled is set and with initial value", async () => {
    const value = "Here is my secret text";
    const { getByTestId } = await render(<SecretTextArea value={value} onChange={emptyFn} disabled />);

    expect(getByTestId("text-input-container")).toHaveClass("disabled");
    expect(getByTestId("secret-text-area-visibility-button")).toBeDisabled();
  });

  it("calls onChange handler when typing", async () => {
    const onChange = jest.fn();
    const value = "Here is my secret text";
    const { getByTestId } = await render(<SecretTextArea onChange={onChange} />);

    const textarea = getByTestId("secret-text-area-text-area");

    userEvent.type(textarea, value);

    expect(onChange).toBeCalledTimes(value.length);
  });

  it("renders on textarea when clicked visibility button", async () => {
    const value = "Here is my secret text";
    const { getByTestId, container } = await render(<SecretTextArea value={value} onChange={emptyFn} />);

    userEvent.click(getByTestId("secret-text-area-visibility-button"));

    expect(getByTestId("secret-text-area-text-area")).toHaveFocus();
    expect(getByTestId("secret-text-area-text-area")).toHaveValue(value);
    expect(container.querySelector('input[type="password"]')).not.toBeInTheDocument();
  });

  it("renders on password input when clicking away from visibility area", async () => {
    const value = "Here is my secret text";
    const { queryByTestId, getByTestId, container } = await render(<SecretTextArea value={value} onChange={emptyFn} />);

    userEvent.click(getByTestId("secret-text-area-visibility-button"));
    expect(getByTestId("secret-text-area-text-area")).toHaveFocus();

    act(() => {
      getByTestId("secret-text-area-text-area").blur();
    });

    expect(container.querySelector("textarea")).not.toBeInTheDocument();
    expect(queryByTestId("secret-text-area-visibility-button")).toBeInTheDocument();
    expect(container.querySelector('input[type="password"]')).toHaveValue(value);
  });
});
