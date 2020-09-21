# Updating Documentation

Our documentation uses [GitBook](https://gitbook.com) and all the [Markdown](https://guides.github.com/features/mastering-markdown/) files are stored in our Github repository.

## Modify on GitHub

1. Start by [forking](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) the repository.
2. Clone the fork on your workstation:

   ```bash
   git clone git@github.com:{YOUR_USERNAME}/airbyte.git
   cd airbyte
   ```

3. Modify the documentation.

All our docs are stored in the `docs` directory. You can use other files as example.

If you're adding new files, don't forget to update `docs/SUMMARY.md`.

Once you're satisfied with your changes just follow the regular PR process.

## For Airbyte's employees

### Edit on GitBook

To update with GitBook, follow these instructions:

1. Create a [new variant](https://docs.gitbook.com/editing-content/variants#create-a-variant). This will create a new branch on [GitHub](https://github.com/airbytehq/airbyte) with the same name
2. Modify the documentation in that new variant
3. Save & merge regularly. Each time you merge, your changes will propagated to your branch. It can take a couple minutes for the changes to show up in [GitHub](https://github.com/airbytehq/airbyte).
4. Once you're satisfied, go on [GitHub](https://github.com/airbytehq/airbyte) and create a PR for your variant branch
5. After the PR is approved, your changes will be merged to `master`
6. Don't forget to remove the branch and the variant once your change has been merged

Just [contact us](mailto:hey@airbyte.io) and we will invite you to our space.

