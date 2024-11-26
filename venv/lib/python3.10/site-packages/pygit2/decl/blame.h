#define GIT_BLAME_OPTIONS_VERSION ...

typedef struct git_blame git_blame;

typedef struct git_blame_options {
	unsigned int version;
	uint32_t flags;
	uint16_t min_match_characters;
	git_oid newest_commit;
	git_oid oldest_commit;
	size_t min_line;
	size_t max_line;
} git_blame_options;

typedef struct git_blame_hunk {
	size_t lines_in_hunk;

	git_oid final_commit_id;
	size_t final_start_line_number;
	git_signature *final_signature;

	git_oid orig_commit_id;
	const char *orig_path;
	size_t orig_start_line_number;
	git_signature *orig_signature;

	char boundary;
} git_blame_hunk;

int git_blame_options_init(
	git_blame_options *opts,
	unsigned int version);

uint32_t git_blame_get_hunk_count(git_blame *blame);
const git_blame_hunk* git_blame_get_hunk_byindex(
		git_blame *blame,
		uint32_t index);

const git_blame_hunk* git_blame_get_hunk_byline(
		git_blame *blame,
		size_t lineno);

int git_blame_file(
		git_blame **out,
		git_repository *repo,
		const char *path,
		git_blame_options *options);

void git_blame_free(git_blame *blame);
