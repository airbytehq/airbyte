import { render } from "utils/testutils";

import { EditorHeader } from "./EditorHeader";

describe("<ArrayOfObjectsEditor />", () => {
  let container: HTMLElement;
  describe("edit mode", () => {
    beforeEach(async () => {
      const renderResult = await render(
        <EditorHeader
          mainTitle={<div data-testid="mainTitle">"This is the main title"</div>}
          addButtonText={<div data-testid="addButtonText">"button text"</div>}
          itemsCount={0}
          onAddItem={() => {
            return null;
          }}
          mode="edit"
        />
      );
      container = renderResult.container;
    });
    test("it renders only relevant items for the mode", () => {
      const mainTitle = container.querySelector("div[data-testid='mainTitle']");
      const addButtonText = container.querySelector("div[data-testid='addButtonText']");
      expect(mainTitle).toBeInTheDocument();
      expect(addButtonText).toBeInTheDocument();
    });
  });
  describe("readonly mode", () => {
    beforeEach(async () => {
      const renderResult = await render(
        <EditorHeader
          mainTitle={<div data-testid="mainTitle">"This is the main title"</div>}
          addButtonText={<div data-testid="addButtonText">"button text"</div>}
          itemsCount={0}
          onAddItem={() => {
            return null;
          }}
          mode="readonly"
        />
      );
      container = renderResult.container;
    });
    test("it renders only relevant items for the mode", () => {
      const mainTitle = container.querySelector("div[data-testid='mainTitle']");
      expect(mainTitle).toBeInTheDocument();
      expect(container.querySelector("div[data-testid='addButtonText']")).not.toBeInTheDocument();
    });
  });
});
