# Code Style

## Configure Java Style for IntelliJ

First, download the style configuration.

```text
curl https://raw.githubusercontent.com/google/styleguide/gh-pages/intellij-java-google-style.xml -o ~/Downloads/intellij-java-google-style.xml
```

Install it in IntelliJ:

1. Go to `Preferences > Editor > Code Style`
2. Press the little cog:
   1. `Import Scheme > IntelliJ IDEA code style XML`
   2. Select the file we just downloaded
3. Select `GoogleStyle` in the dropdown
4. Change default `Hard wrap at` in `Wrapping and Braces` tab to **150**.
5. We prefer `import foo.bar.ClassName` over `import foo.bar.*`. Even in cases where we import multiple classes from the same package. This can be set by going to `Preferences > Code Style > Java > Imports` and changing `Class count to use import with '*'` to 9999 and \`Names count to use static import with '\*' to 9999.
6. You're done!
