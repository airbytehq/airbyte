# Updating Documentation

Our documentation uses [GitBook](https://gitbook.com) and all the [Markdown](https://guides.github.com/features/mastering-markdown/) files are stored in our Github repository.

There are 3 different ways you can update the documentation.

## `Edit on GitHub` link

On the documentation page you want to update, just click the `Edit on GitHub` link in right panel. 

That will get you directly to the file on GitHub. You can use GitHub's editor to update the file. Once you're satisfied with your change you can submit a PR.

We recommend that method for changes limited to one file \(typos, minor updates\).

## Modify the repository

```bash
$ git clone git@github.com:datalineio/dataline.git
```

All our docs are stored in the `docs` directory. You can use other files as example.

If you're adding new files, don't forget to update `docs/SUMMARY.md`.

Once you're satisfied with your changes just follow the regular PR process.

## Edit on GitBook

To update with GitBook, follow these instructions:

1. Create a [new variant](https://docs.gitbook.com/editing-content/variants#create-a-variant). This will create a new branch on [GitHub](https://github.com/datalineio/dataline) with the same name
2. Modify the documentation in that new variant
3. Save & merge regularly
4. Once you're satisfied, go on [GitHub](https://github.com/datalineio/dataline) and create a PR for your variant branch
5. After the PR is approved, your changes will be merged to `master`
6. Don't forget to remove the branch and the variant once your change has been merged

Just [contact us](mailto:hey@dataline.io) and we will invite you to our space.

