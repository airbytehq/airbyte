import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";

import { TagInput } from "./TagInput";

const TagInputWithWrapper = () => {
  const [fieldValue, setFieldValue] = useState(["tag1", "tag2"]);
  return <TagInput name="test" fieldValue={fieldValue} onChange={(values) => setFieldValue(values)} disabled={false} />;
};

describe("<TagInput />", () => {
  it("renders with defaultValue", () => {
    render(<TagInputWithWrapper />);
    const tag1 = screen.getByText("tag1");
    const tag2 = screen.getByText("tag2");
    expect(tag1).toBeInTheDocument();
    expect(tag2).toBeInTheDocument();
  });

  describe("delimiters and keypress events create tags", () => {
    it("adds a tag when user types a tag and hits enter", () => {
      render(<TagInputWithWrapper />);
      const input = screen.getByRole("combobox");
      userEvent.type(input, "tag3{enter}");
      const tag3 = screen.getByText("tag3");
      expect(tag3).toBeInTheDocument();
    });
    it("adds a tag when user types a tag and hits tab", () => {
      render(<TagInputWithWrapper />);
      const input = screen.getByRole("combobox");
      userEvent.type(input, "tag3{Tab}");
      const tag3 = screen.getByText("tag3");
      expect(tag3).toBeInTheDocument();
    });

    it("adds multiple tags when a user enters a string with commas", () => {
      render(<TagInputWithWrapper />);
      const input = screen.getByRole("combobox");
      userEvent.type(input, "tag3, tag4,");
      const tag3 = screen.getByText("tag3");
      expect(tag3).toBeInTheDocument();
      const tag4 = screen.getByText("tag4");
      expect(tag4).toBeInTheDocument();
    });
    it("adds multiple tags when a user enters a string with semicolons", () => {
      render(<TagInputWithWrapper />);
      const input = screen.getByRole("combobox");
      userEvent.type(input, "tag3; tag4;");
      const tag3 = screen.getByText("tag3");
      expect(tag3).toBeInTheDocument();
      const tag4 = screen.getByText("tag4");
      expect(tag4).toBeInTheDocument();
    });
    it("handles a combination of methods at once", () => {
      render(<TagInputWithWrapper />);
      const input = screen.getByRole("combobox");
      userEvent.type(input, "tag3; tag4{Tab} tag5, tag6{enter}");
      const tag3 = screen.getByText("tag3");
      expect(tag3).toBeInTheDocument();
      const tag4 = screen.getByText("tag4");
      expect(tag4).toBeInTheDocument();
      const tag5 = screen.getByText("tag5");
      expect(tag5).toBeInTheDocument();
      const tag6 = screen.getByText("tag6");
      expect(tag6).toBeInTheDocument();
    });
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
});
