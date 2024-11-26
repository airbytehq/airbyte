typedef struct {
	char *ptr;
	size_t reserved;
	size_t size;
} git_buf;

void git_buf_dispose(git_buf *buffer);
