# Frontend Style Guide

This serves as a living document regarding conventions we have agreed upon as a frontend team. In general, the aim of these decisions and discussions is to both (a) increase the readability and consistency of our code and (b) decrease day to day decision-making so we can spend more time writing better code.  

## General Code Style and Formatting

* Where possible, we rely on automated systems to maintain consistency in code style 
* We use eslint, Prettier, and VSCode settings to automate these choices.  The configuration files for these are checked into our repository, so no individual setup should be required beyond ensuring your VSCode settings include: 

```
"editor.codeActionsOnSave": {
  "source.fixAll.eslint": true,
}
```

* Don’t use single-character names. Using meaningful name for function parameters is a way of making the code self-documented and we always should do it. Example:
    * .filter(([key, value]) => isDefined(value.default) ✅
    * .filter(([k, v]) => isDefined(v.default) ❌


## Exporting

* Export at declaration, not at the bottom. For example:
    * export const myVar ✅
    * const myVar; export { myVar }; ❌


## Component Props
* Use explicit, verbose naming 
    * ie: `interface ConnectionFormProps` not `interface iProps`


## Testing

* Test files should be store alongside the files/features they are testing
* Use the prop `data-testid` instead of `data-id`


## Types

* For component props, prefer type unions over enums:
    * `type SomeType = “some” | “type”;` ✅
    * `enum SomeEnum = { SOME: “some”, TYPE: “type” };` ❌
    * Exceptions may include:
        * Generated using enums from the API
        * When the value on an enum is cleaner than the string
            * In this case use `const enum` instead

