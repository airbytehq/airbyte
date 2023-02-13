import { render } from "test-utils/testutils";

import { EditorHeader } from "./EditorHeader";

describe("<ArrayOfObjectsEditor />", () => {
  let container: HTMLElement;
  describe("edit mode", () => {
    it("renders only relevant items for the mode", async () => {
      const renderResult = await render(
        <EditorHeader
          mainTitle={<div data-testid="main-title">"This is the main title"</div>}
          addButtonText={<div data-testid="add-button-text">"button text"</div>}
          itemsCount={0}
          onAddItem={() => {
            return null;
          }}
          mode="edit"
        />
      );
      container = renderResult.container;
      const mainTitle = container.querySelector("div[data-testid='main-title']");
      const addButtonText = container.querySelector("div[data-testid='add-button-text']");
      expect(mainTitle).toBeInTheDocument();
      expect(addButtonText).toBeInTheDocument();
    });
  });
  describe("readonly mode", () => {
    it("renders only relevant items for the mode", async () => {
      const renderResult = await render(
        <EditorHeader
          mainTitle={<div data-testid="main-title">"This is the main title"</div>}
          addButtonText={<div data-testid="add-button-text">"button text"</div>}
          itemsCount={0}
          onAddItem={() => {
            return null;
          }}
          mode="readonly"
        />
      );
      container = renderResult.container;
      const mainTitle = container.querySelector("div[data-testid='main-title']");
      expect(mainTitle).toBeInTheDocument();
      expect(container.querySelector("div[data-testid='add-button-text']")).not.toBeInTheDocument();
    });
  });
});
