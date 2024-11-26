#define GIT_MERGE_OPTIONS_VERSION 1

typedef enum {
	GIT_MERGE_FIND_RENAMES = 1,
	GIT_MERGE_FAIL_ON_CONFLICT = 2,
	GIT_MERGE_SKIP_REUC = 4,
	GIT_MERGE_NO_RECURSIVE = 8,
} git_merge_flag_t;

typedef enum {
	GIT_MERGE_FILE_FAVOR_NORMAL = 0,
	GIT_MERGE_FILE_FAVOR_OURS = 1,
	GIT_MERGE_FILE_FAVOR_THEIRS = 2,
	GIT_MERGE_FILE_FAVOR_UNION = 3,
} git_merge_file_favor_t;

typedef enum {
	GIT_MERGE_FILE_DEFAULT = 0,
	GIT_MERGE_FILE_STYLE_MERGE = 1,
	GIT_MERGE_FILE_STYLE_DIFF3 = 2,
	GIT_MERGE_FILE_SIMPLIFY_ALNUM = 4,
	GIT_MERGE_FILE_IGNORE_WHITESPACE = 8,
	GIT_MERGE_FILE_IGNORE_WHITESPACE_CHANGE = 16,
	GIT_MERGE_FILE_IGNORE_WHITESPACE_EOL = 32,
	GIT_MERGE_FILE_DIFF_PATIENCE = 64,
	GIT_MERGE_FILE_DIFF_MINIMAL = 128,
} git_merge_file_flag_t;

typedef struct {
	unsigned int version;
	git_merge_flag_t flags;
	unsigned int rename_threshold;
	unsigned int target_limit;
	git_diff_similarity_metric *metric;
	unsigned int recursion_limit;
	const char *default_driver;
	git_merge_file_favor_t file_favor;
	git_merge_file_flag_t file_flags;
} git_merge_options;

typedef struct {
	unsigned int automergeable;
	const char *path;
	unsigned int mode;
	const char *ptr;
	size_t len;
} git_merge_file_result;

typedef struct {
	unsigned int version;
	const char *ancestor_label;
	const char *our_label;
	const char *their_label;
	git_merge_file_favor_t favor;
	git_merge_file_flag_t flags;
	unsigned short marker_size;
} git_merge_file_options;

int git_merge_options_init(
	git_merge_options *opts,
	unsigned int version);

int git_merge_commits(
	git_index **out,
	git_repository *repo,
	const git_commit *our_commit,
	const git_commit *their_commit,
	const git_merge_options *opts);

int git_merge_trees(
	git_index **out,
	git_repository *repo,
	const git_tree *ancestor_tree,
	const git_tree *our_tree,
	const git_tree *their_tree,
	const git_merge_options *opts);

int git_merge_file_from_index(
	git_merge_file_result *out,
	git_repository *repo,
	const git_index_entry *ancestor,
	const git_index_entry *ours,
	const git_index_entry *theirs,
	const git_merge_file_options *opts);

int git_merge(
	git_repository *repo,
	const git_annotated_commit **their_heads,
	size_t their_heads_len,
	const git_merge_options *merge_opts,
	const git_checkout_options *checkout_opts);

void git_merge_file_result_free(git_merge_file_result *result);
