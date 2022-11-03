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
4. Change default `Hard wrap at` in `Wrapping and Braces` tab to **150**
5. Use explicit imports (example: `import foo.bar.ClassName` over `import foo.bar.*`) even when importing multiple classes from the same package. This can be set by going to `Preferences > Code Style > Java > Imports` and changing `Class count to use import with '*'` to `9999` and `Names count to use static import with '\*'` to `9999`
6. Add the `final` keyword wherever possible. You can either set this as the default for your IDE or you can set it just for the Airbyte project(s) that you are using
   1. Turn on the inspection. Go into `Preferences > Editor > Inspections`
      1. Search `"Field may be 'final'"` > check the box
      2. Search `"local variable or parameter can be 'final'"` > check the box
      3. Apply the changes
   2. Turn on the auto add final. Go into IntelliJ Preferences
      1. Plugins - install Save Actions if not already installed
      2. Go to Save Actions in the preferences [left navigation column](../assets/docs/save_actions_settings.png) (NOT Tools > Actions on Save -- that is a different tool)
         1. `Activate save actions on save` > check the box
         2. `Active save actions on shortcut` > check the box
         3. `Activate save actions on batch` > check the box
         4. `Add final modifier to field` > check the box
         5. `Add final modifier to local variable or parameter` > check the box
         6. Apply the changes
7. You're done!

## Source code comments

It's hard to pin down exactly what to do around source code comments, but there are two \(very subjective\) and rough guidelines:

**If something is not obvious, write it down**. Examples include:

* non-trivial class definitions should have docstrings
* magic variables should have comments explaining why those values are used \(e.g: if using a page size of 10 in a connector, describe why if possible. If there is no reason, that's also fine, just mention in a comment\).
* Complicated subroutines/logic which cannot be refactored should have comments explaining what they are doing and why

**If something is obvious, don't write it down** since it's probably more likely to go out of date. For example, a comment like `x = 42; // sets x to 42` is not adding any new information and is therefore better omitted.
