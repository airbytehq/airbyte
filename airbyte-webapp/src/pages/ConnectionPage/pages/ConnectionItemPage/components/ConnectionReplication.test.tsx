import { render } from "@testing-library/react";

import { ConnectionReplication } from "./ConnectionReplication";

describe("ConnectionReplication", () => {
  it("should render", () => {
    // TODO: Wrapper component
    expect(render(<ConnectionReplication />)).toMatchSnapshot();
  });
});
