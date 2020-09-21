# Updating Documentation

Our documentation uses [GitBook](https://gitbook.com), and all the [Markdown](https://guides.github.com/features/mastering-markdown/) files are stored in our Github repository.

There are 3 different ways you can update the documentation. But only one is available to the community. The 2 others are only available to the Airbyte team. 

## 1. Modify the repository \(available to everyone\)

```bash
$ git clone git@github.com:airbytehq/airbyte.git
```

All our docs are stored in the `docs` directory. You can use other files as examples.

If you're adding new files, don't forget to update `docs/SUMMARY.md`.

Once you're satisfied with your changes, just follow the regular PR process.

## 2. `Edit on GitHub` link \(available to the Airbyte team only\)

On the documentation page you want to update, just click the `Edit on GitHub` link in the right panel.

That will get you directly to the file on GitHub. You can use GitHub's editor to update the file. Once you're satisfied with your change you can submit a PR.

We recommend that method for changes limited to one file \(typos, minor updates\).

## 3. Edit on GitBook \(available to the Airbyte team only\)

To update with GitBook, follow these instructions:

1. Create a [new variant](https://docs.gitbook.com/editing-content/variants#create-a-variant). This will create a new branch on [GitHub](https://github.com/airbytehq/airbyte) with the same name. 
2. Modify the documentation, as you see fit on all pages, in that new variant.
3. Save & merge regularly. Each time you merge, your changes will propagate to your branch. It can take a couple minutes for the changes to show up in [GitHub](https://github.com/airbytehq/airbyte).
4. Once you're satisfied, go on [GitHub](https://github.com/airbytehq/airbyte) and create a PR for your variant branch.
5. After the PR is approved, your changes will be merged to `master`. 
6. Don't forget to remove the branch and the variant once your change has been merged.

Just [contact us](mailto:hey@airbyte.io) and we will invite you to our space.

