typedef struct git_strarray {
	char **strings;
	size_t count;
} git_strarray;

void git_strarray_free(git_strarray *array);
