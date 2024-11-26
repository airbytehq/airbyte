typedef struct git_config_iterator git_config_iterator;

typedef enum {
	GIT_CONFIG_LEVEL_PROGRAMDATA = 1,
	GIT_CONFIG_LEVEL_SYSTEM = 2,
	GIT_CONFIG_LEVEL_XDG = 3,
	GIT_CONFIG_LEVEL_GLOBAL = 4,
	GIT_CONFIG_LEVEL_LOCAL = 5,
	GIT_CONFIG_LEVEL_APP = 6,
	GIT_CONFIG_HIGHEST_LEVEL = -1,
} git_config_level_t;

typedef struct git_config_entry {
	const char *name;
	const char *value;
	unsigned int include_depth;
	git_config_level_t level;
	void (*free)(struct git_config_entry *entry);
	void *payload;
} git_config_entry;

void git_config_entry_free(git_config_entry *);
void git_config_free(git_config *cfg);
int git_config_get_entry(
	git_config_entry **out,
	const git_config *cfg,
	const char *name);

int git_config_get_string(const char **out, const git_config *cfg, const char *name);
int git_config_set_string(git_config *cfg, const char *name, const char *value);
int git_config_set_bool(git_config *cfg, const char *name, int value);
int git_config_set_int64(git_config *cfg, const char *name, int64_t value);
int git_config_parse_bool(int *out, const char *value);
int git_config_parse_int64(int64_t *out, const char *value);
int git_config_delete_entry(git_config *cfg, const char *name);
int git_config_add_file_ondisk(
	git_config *cfg,
	const char *path,
	git_config_level_t level,
	const git_repository *repo,
	int force);
int git_config_iterator_new(git_config_iterator **out, const git_config *cfg);
int git_config_next(git_config_entry **entry, git_config_iterator *iter);
void git_config_iterator_free(git_config_iterator *iter);
int git_config_multivar_iterator_new(git_config_iterator **out, const git_config *cfg, const char *name, const char *regexp);
int git_config_set_multivar(git_config *cfg, const char *name, const char *regexp, const char *value);
int git_config_delete_multivar(git_config *cfg, const char *name, const char *regexp);
int git_config_new(git_config **out);
int git_config_snapshot(git_config **out, git_config *config);
int git_config_open_ondisk(git_config **out, const char *path);
int git_config_find_system(git_buf *out);
int git_config_find_global(git_buf *out);
int git_config_find_xdg(git_buf *out);
