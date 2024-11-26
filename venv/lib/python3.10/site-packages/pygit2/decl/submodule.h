#define GIT_SUBMODULE_UPDATE_OPTIONS_VERSION ...

typedef struct git_submodule_update_options {
	unsigned int version;
	git_checkout_options checkout_opts;
	git_fetch_options fetch_opts;
	int allow_fetch;
} git_submodule_update_options;

int git_submodule_update_options_init(
	git_submodule_update_options *opts, unsigned int version);

int git_submodule_add_setup(
	git_submodule **out,
	git_repository *repo,
	const char *url,
	const char *path,
	int use_gitlink);
int git_submodule_clone(
	git_repository **out,
	git_submodule *submodule,
	const git_submodule_update_options *opts);
int git_submodule_add_finalize(git_submodule *submodule);

int git_submodule_update(git_submodule *submodule, int init, git_submodule_update_options *options);

int git_submodule_lookup(
	git_submodule **out,
	git_repository *repo,
	const char *name);

void git_submodule_free(git_submodule *submodule);
int git_submodule_open(git_repository **repo, git_submodule *submodule);
int git_submodule_init(git_submodule *submodule, int overwrite);
int git_submodule_reload(git_submodule *submodule, int force);

const char * git_submodule_name(git_submodule *submodule);
const char * git_submodule_path(git_submodule *submodule);
const char * git_submodule_url(git_submodule *submodule);
const char * git_submodule_branch(git_submodule *submodule);
const git_oid * git_submodule_head_id(git_submodule *submodule);

int git_submodule_status(unsigned int *status, git_repository *repo, const char *name, git_submodule_ignore_t ignore);
