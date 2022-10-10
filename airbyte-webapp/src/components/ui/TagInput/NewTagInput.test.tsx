import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";

import { NewTagInput } from "./NewTagInput";

const TagInputWithWrapper = () => {
  const [fieldValue, setFieldValue] = useState(["tag1", "tag2"]);
  return (
    <NewTagInput name="test" fieldValue={fieldValue} onChange={(values) => setFieldValue(values)} disabled={false} />
  );
};

it("renders with defaultValue", () => {
  render(<TagInputWithWrapper />);
  const tag1 = screen.getByText("tag1");
  const tag2 = screen.getByText("tag2");
  expect(tag1).toBeInTheDocument();
  expect(tag2).toBeInTheDocument();
});

it("adds a tag when user types a tag and hits enter", () => {
  render(<TagInputWithWrapper />);
  const input = screen.getByRole("combobox");
  userEvent.type(input, "tag3{enter}");
  const tag3 = screen.getByText("tag3");
  expect(tag3).toBeInTheDocument();
});

it("correctly removes a tag when user clicks its Remove button", () => {
  render(<TagInputWithWrapper />);
  const tag1 = screen.getByText("tag1");
  expect(tag1).toBeInTheDocument();

  const tag2 = screen.getByText("tag2");
  expect(tag2).toBeInTheDocument();

  const input = screen.getByRole("combobox");
  userEvent.type(input, "tag3{enter}");
  const tag3 = screen.getByText("tag3");
  expect(tag3).toBeInTheDocument();
  const removeTag2Button = screen.getByRole("button", { name: "Remove tag2" });
  userEvent.click(removeTag2Button);

  const tag1again = screen.getByText("tag1");
  expect(tag1again).toBeInTheDocument();

  // queryBy because getBy will throw if not in the DOM
  const tag2again = screen.queryByText("tag2");
  expect(tag2again).not.toBeInTheDocument();

  const tag3again = screen.getByText("tag3");
  expect(tag3again).toBeInTheDocument();
});
