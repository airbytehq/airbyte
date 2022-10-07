import { render, screen } from "@testing-library/react";
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
  const tag2 = screen.getAllByText("tag2");
  expect(tag1).toBeInTheDocument();
  expect(tag2).toBeInTheDocument();
});
