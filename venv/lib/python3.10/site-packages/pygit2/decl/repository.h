#define GIT_REPOSITORY_INIT_OPTIONS_VERSION ...

void git_repository_free(git_repository *repo);
int git_repository_state_cleanup(git_repository *repo);
int git_repository_config(git_config **out, git_repository *repo);
int git_repository_config_snapshot(git_config **out, git_repository *repo);

typedef enum {
	GIT_REPOSITORY_INIT_BARE              = 1,
	GIT_REPOSITORY_INIT_NO_REINIT         = 2,
	GIT_REPOSITORY_INIT_NO_DOTGIT_DIR     = 4,
	GIT_REPOSITORY_INIT_MKDIR             = 8,
	GIT_REPOSITORY_INIT_MKPATH            = 16,
	GIT_REPOSITORY_INIT_EXTERNAL_TEMPLATE = 32,
	GIT_REPOSITORY_INIT_RELATIVE_GITLINK  = 64,
} git_repository_init_flag_t;

typedef enum {
	GIT_REPOSITORY_INIT_SHARED_UMASK = 0,
	GIT_REPOSITORY_INIT_SHARED_GROUP = 0002775,
	GIT_REPOSITORY_INIT_SHARED_ALL   = 0002777,
} git_repository_init_mode_t;

typedef enum {
	GIT_REPOSITORY_STATE_NONE,
	GIT_REPOSITORY_STATE_MERGE,
	GIT_REPOSITORY_STATE_REVERT,
	GIT_REPOSITORY_STATE_REVERT_SEQUENCE,
	GIT_REPOSITORY_STATE_CHERRYPICK,
	GIT_REPOSITORY_STATE_CHERRYPICK_SEQUENCE,
	GIT_REPOSITORY_STATE_BISECT,
	GIT_REPOSITORY_STATE_REBASE,
	GIT_REPOSITORY_STATE_REBASE_INTERACTIVE,
	GIT_REPOSITORY_STATE_REBASE_MERGE,
	GIT_REPOSITORY_STATE_APPLY_MAILBOX,
	GIT_REPOSITORY_STATE_APPLY_MAILBOX_OR_REBASE
} git_repository_state_t;

typedef struct {
	unsigned int version;
	uint32_t    flags;
	uint32_t    mode;
	const char *workdir_path;
	const char *description;
	const char *template_path;
	const char *initial_head;
	const char *origin_url;
} git_repository_init_options;

int git_repository_init_options_init(
	git_repository_init_options *opts,
	unsigned int version);

int git_repository_init(
	git_repository **out,
	const char *path,
	unsigned is_bare);

int git_repository_init_ext(
	git_repository **out,
	const char *repo_path,
	git_repository_init_options *opts);

typedef enum {
	GIT_REPOSITORY_OPEN_NO_SEARCH = 1,
	GIT_REPOSITORY_OPEN_CROSS_FS  = 2,
	GIT_REPOSITORY_OPEN_BARE      = 4,
	GIT_REPOSITORY_OPEN_NO_DOTGIT = 8,
	GIT_REPOSITORY_OPEN_FROM_ENV  = 16,
} git_repository_open_flag_t;

int git_repository_open_ext(
	git_repository **out,
	const char *path,
	unsigned int flags,
	const char *ceiling_dirs);

int git_repository_set_head(
	git_repository* repo,
	const char* refname);

int git_repository_set_head_detached(
	git_repository* repo,
	const git_oid* commitish);

int git_repository_ident(const char **name, const char **email, const git_repository *repo);
int git_repository_set_ident(git_repository *repo, const char *name, const char *email);
int git_repository_index(git_index **out, git_repository *repo);
git_repository_state_t git_repository_state(git_repository *repo);

int git_repository_submodule_cache_all(git_repository *repo);
int git_repository_submodule_cache_clear(git_repository *repo);
