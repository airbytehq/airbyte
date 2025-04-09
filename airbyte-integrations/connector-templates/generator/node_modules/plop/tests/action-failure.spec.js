import { resolve, dirname } from "node:path";
import { waitFor } from "cli-testing-library";
import { renderPlop } from "./render.js";

import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

test("should exit with code 1 when failed actions", async () => {
  const { findByText, userEvent } = await renderPlop([], {
    cwd: resolve(__dirname, "./examples/action-failure"),
  });
  expect(await findByText("What is your name?")).toBeInTheConsole();
  userEvent.keyboard("Joe");
  expect(await findByText("Joe")).toBeInTheConsole();
  userEvent.keyboard("[Enter]");
  const actionOutput = await findByText("Action failed");
  await waitFor(() =>
    expect(actionOutput.hasExit()).toStrictEqual({ exitCode: 1 })
  );
});
