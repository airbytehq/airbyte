import { resolve, dirname } from "node:path";
import { renderPlop } from "./render.js";

import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

test("should load ESM file", async () => {
  const { findByText, userEvent } = await renderPlop([], {
    cwd: resolve(__dirname, "./examples/esm"),
  });
  expect(await findByText("What is your name?")).toBeInTheConsole();
  userEvent.keyboard("Joe");
  expect(await findByText("Joe")).toBeInTheConsole();
  userEvent.keyboard("[Enter]");
});

test("should load MJS file", async () => {
  const { findByText, userEvent } = await renderPlop([], {
    cwd: resolve(__dirname, "./examples/mjs"),
  });
  expect(await findByText("What is your name?")).toBeInTheConsole();
  userEvent.keyboard("Joe");
  expect(await findByText("Joe")).toBeInTheConsole();
  userEvent.keyboard("[Enter]");
});

test("should load CJS file", async () => {
  const { findByText, userEvent } = await renderPlop([], {
    cwd: resolve(__dirname, "./examples/cjs"),
  });
  expect(await findByText("What is your name?")).toBeInTheConsole();
  userEvent.keyboard("Joe");
  expect(await findByText("Joe")).toBeInTheConsole();
  userEvent.keyboard("[Enter]");
});

test("should load JS module='commonjs' file", async () => {
  const { findByText, userEvent } = await renderPlop([], {
    cwd: resolve(__dirname, "./examples/cjs-js"),
  });
  expect(await findByText("What is your name?")).toBeInTheConsole();
  userEvent.keyboard("Joe");
  expect(await findByText("Joe")).toBeInTheConsole();
  userEvent.keyboard("[Enter]");
});
