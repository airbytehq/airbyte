# Frontend Style Guide

This serves as a living document regarding conventions we have agreed upon as a frontend team. In general, the aim of these decisions and discussions is to both (a) increase the readability and consistency of our code and (b) decrease day to day decision-making so we can spend more time writing better code.

## General Code Style and Formatting

- Where possible, we rely on automated systems to maintain consistency in code style
- We use eslint, Prettier, and VSCode settings to automate these choices. The configuration files for these are checked into our repository, so no individual setup should be required beyond ensuring your VSCode settings include:

```
"editor.codeActionsOnSave": {
  "source.fixAll.eslint": true,
}
```

- Don’t use single-character names. Using meaningful name for function parameters is a way of making the code self-documented and we always should do it. Example:
  - .filter(([key, value]) => isDefined(value.default) ✅
  - .filter(([k, v]) => isDefined(v.default) ❌

## Exporting

- Export at declaration, not at the bottom. For example:
  - export const myVar ✅
  - const myVar; export { myVar }; ❌

## Component Props

- Use explicit, verbose naming
  - ie: `interface ConnectionFormProps` not `interface iProps`

## Testing

- Test files should be store alongside the files/features they are testing
- Use the prop `data-testid` instead of `data-id`

## Types

- For component props, prefer type unions over enums:
  - `type SomeType = “some” | “type”;` ✅
  - `enum SomeEnum = { SOME: “some”, TYPE: “type” };` ❌
  - Exceptions may include:
    - Generated using enums from the API
    - When the value on an enum is cleaner than the string
      - In this case use `const enum` instead

## Styling

### Color variables cannot be used inside of rgba() functions

Our SCSS color variables compile to `rgb(X, Y, Z)`, which is an invalid value in the CSS `rgba()` function. A custom stylelint rule, `airbyte/no-color-variables-in-rgba`, enforces this rule.

❌ Incorrect

```scss
@use "scss/colors";

.myClass {
  background-color: rgba(colors.$blue-400, 50%);
}
```

✅ Correct - define a color variable with transparency and use it directly

```scss
@use "scss/colors";

.myClass {
  background-color: colors.$blue-transparent;
}
```

> Historical context: previously there was some usage of color variables inside `rgba()` functions. In these cases, _SASS_ was actually compiling this into CSS for us, because it knew to convert `rgba(rgb(255, 0, 0), 50%)` into `rgb(255, 0, 0, 50%)`. Now that we use CSS Custom Properties for colors, SASS cannot know the value of the color variable at build time. So it outputs `rgba(var(--blue), 50%)` which will not work as expected.

## Folder Structure

TODO: Summarize the rest beside react components.

## React Components

> The Airbyte team is currently restructuring how components are organized in the codebase. Components currently in `src/views/` are being be migrated to `src/components/`. `src/components` is currently being reorganized. The new structure is described below and it's expected that new code follows the new structure.

Most React components are in `src/components` but components that represent pages on the site are in `src/pages`. 

### Components Structure

The `src/components` folder is divided into sub-folders for each domain in the app such as `connection`, `source`, and `destination`. Core UI components (such as Buttons, tables, etc.) are all located in `src/components/ui`. Components that are shared across different domains but may not be part of the UI library are in `src/components/common`. Sub-folders must be written in `camelCase`.

Within each sub-folder, there are folder for each major component. These folders are written in `PascalCase`, the same way a React component would be named. Within these folders there are a few files:

* `index.ts` - Used to the main component and supporting functions or types to the app.
* `{MainComponentName}.tsx` - The main component, also exported through `index.ts`
* `{MainComponentName}.test.tsx` - The test file
* `{MainComponentName}.module.scss` - The main component's style file
* Files for additional components that support the main Component directly, using the same naming conventions as above.
* `types.ts` (optional) - Types shared between different sub-components
* `utils.ts` (optional) - Any utilities that support the components

When using supporting components, the folder could become rather full of them. In those cases Components should be split into their own folders parallel to the main component, especially when the supporting component also needs to be broken down into multiple sub components.

Here's a hypothetical example: The app has a streams panel with a lot of sub-components including a streams table. Instead of placing all the components under `src/components/connection/StreamsPanel`, the table should be broken out into it's own sub-folder as a child of the `connection` folder.

```
// Don't:

src/
  components/
    connection/
      StreamsPanel/
        index.ts
        StreamsPanel.tsx
        StreamsPanelHeader.tsx
        StreamsPanelContent.tsx
        StreamsTable.tsx
        StreamsTableBody.tsx
        StreamsTableCell.tsx
        StreamsTableHeader.tsx
        StreamsTableRow.tsx

// Do:

src/
  components/
    connection/
      StreamsPanel/
        index.ts
        StreamsPanel.tsx
        StreamsPanelHeader.tsx
        StreamsPanelContent.tsx
      StreamsTable/
        index.ts
        StreamsTable.tsx
        StreamsTableBody.tsx
        StreamsTableCell.tsx
        StreamsTableHeader.tsx
        StreamsTableRow.tsx
```

### Pages Structure

TODO
