typedef enum {
	GIT_DESCRIBE_DEFAULT,
	GIT_DESCRIBE_TAGS,
	GIT_DESCRIBE_ALL,
} git_describe_strategy_t;

typedef struct git_describe_options {
	unsigned int version;
	unsigned int max_candidates_tags;
	unsigned int describe_strategy;
	const char *pattern;
	int only_follow_first_parent;
	int show_commit_oid_as_fallback;
} git_describe_options;

#define GIT_DESCRIBE_OPTIONS_VERSION 1

int git_describe_options_init(git_describe_options *opts, unsigned int version);

typedef struct {
	unsigned int version;
	unsigned int abbreviated_size;
	int always_use_long_format;
	const char *dirty_suffix;
} git_describe_format_options;

#define GIT_DESCRIBE_FORMAT_OPTIONS_VERSION 1

int git_describe_init_format_options(git_describe_format_options *opts, unsigned int version);

typedef struct git_describe_result git_describe_result;

int git_describe_commit(
	git_describe_result **result,
	git_object *committish,
	git_describe_options *opts);

int git_describe_workdir(
	git_describe_result **out,
	git_repository *repo,
	git_describe_options *opts);

int git_describe_format(
	git_buf *out,
	const git_describe_result *result,
	const git_describe_format_options *opts);

void git_describe_result_free(git_describe_result *result);
