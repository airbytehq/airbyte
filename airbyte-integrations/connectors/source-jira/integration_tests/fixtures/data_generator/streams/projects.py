from ..base import BaseStream


class Projects(BaseStream):
    list_endpoint = 'project/search'
    generate_endpoint = 'project'

    def extract(self, response):
        if response.status_code == 404:
            issues = []
        else:
            issues = response.json().get("values")
        return issues

    def list(self):
        params = {}
        url = self.get_url(endpoint=self.list_endpoint)
        for project in self.fetch_data(url, params):
            yield project

    def generate(self):
        pass


class ProjectRelatedMixin:
    def __init__(self):
        self.projects = Projects()
        super(ProjectRelatedMixin, self).__init__()

    def get_projects(self):
        projects_batch = self.projects.list()
        return projects_batch


