# Updating Documentation

Our documentation uses [GitBook](https://gitbook.com), and all the [Markdown](https://guides.github.com/features/mastering-markdown/) files are stored in our Github repository.

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
