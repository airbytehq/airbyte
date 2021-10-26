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
6. We add the `final` keyword wherever possible. It's a drag to have to do it manually, however, so we set up the IDE to do it for us. You can either set this as the default for your IDE or you can set it just for the Airbyte project(s) that you are using.
   1. Turn on the inspection. Go into IntelliJ Preferences...
      1. Editor > Inspections > Search (with the quotation marks included) "Field may be 'final'" > check the box
      2. Editor > Inspections > Search "local variable or parameter may be final" > check the box
      3. Apply the changes.
   2. Turn on the auto add final. Go into IntelliJ Preferences...
      1. Plugins - install Save Actions if not already installed.
      2. Go to Save Actions in the preferences left nav (NOT Tools > Actions on Save -- that is a different tool)
         1. Activate save actions on save > check the box
         2. Active save actions on shortcut > check the box
         3. Activate save actions on batch > check the box
         4. Add final modifier to field > check the box
         5. Add final modifier to local variable or parameter > check the box
         6. Apply the changes.
7. You're done!
