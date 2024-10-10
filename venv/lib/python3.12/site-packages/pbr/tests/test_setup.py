# Copyright (c) 2011 OpenStack Foundation
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import print_function

import os

try:
    import cStringIO as io
    BytesIO = io.StringIO
except ImportError:
    import io
    BytesIO = io.BytesIO

import fixtures

from pbr import git
from pbr import options
from pbr.tests import base


class SkipFileWrites(base.BaseTestCase):

    scenarios = [
        ('changelog_option_true',
         dict(option_key='skip_changelog', option_value='True',
              env_key='SKIP_WRITE_GIT_CHANGELOG', env_value=None,
              pkg_func=git.write_git_changelog, filename='ChangeLog')),
        ('changelog_option_false',
         dict(option_key='skip_changelog', option_value='False',
              env_key='SKIP_WRITE_GIT_CHANGELOG', env_value=None,
              pkg_func=git.write_git_changelog, filename='ChangeLog')),
        ('changelog_env_true',
         dict(option_key='skip_changelog', option_value='False',
              env_key='SKIP_WRITE_GIT_CHANGELOG', env_value='True',
              pkg_func=git.write_git_changelog, filename='ChangeLog')),
        ('changelog_both_true',
         dict(option_key='skip_changelog', option_value='True',
              env_key='SKIP_WRITE_GIT_CHANGELOG', env_value='True',
              pkg_func=git.write_git_changelog, filename='ChangeLog')),
        ('authors_option_true',
         dict(option_key='skip_authors', option_value='True',
              env_key='SKIP_GENERATE_AUTHORS', env_value=None,
              pkg_func=git.generate_authors, filename='AUTHORS')),
        ('authors_option_false',
         dict(option_key='skip_authors', option_value='False',
              env_key='SKIP_GENERATE_AUTHORS', env_value=None,
              pkg_func=git.generate_authors, filename='AUTHORS')),
        ('authors_env_true',
         dict(option_key='skip_authors', option_value='False',
              env_key='SKIP_GENERATE_AUTHORS', env_value='True',
              pkg_func=git.generate_authors, filename='AUTHORS')),
        ('authors_both_true',
         dict(option_key='skip_authors', option_value='True',
              env_key='SKIP_GENERATE_AUTHORS', env_value='True',
              pkg_func=git.generate_authors, filename='AUTHORS')),
    ]

    def setUp(self):
        super(SkipFileWrites, self).setUp()
        self.temp_path = self.useFixture(fixtures.TempDir()).path
        self.root_dir = os.path.abspath(os.path.curdir)
        self.git_dir = os.path.join(self.root_dir, ".git")
        if not os.path.exists(self.git_dir):
            self.skipTest("%s is missing; skipping git-related checks"
                          % self.git_dir)
            return
        self.filename = os.path.join(self.temp_path, self.filename)
        self.option_dict = dict()
        if self.option_key is not None:
            self.option_dict[self.option_key] = ('setup.cfg',
                                                 self.option_value)
        self.useFixture(
            fixtures.EnvironmentVariable(self.env_key, self.env_value))

    def test_skip(self):
        self.pkg_func(git_dir=self.git_dir,
                      dest_dir=self.temp_path,
                      option_dict=self.option_dict)
        self.assertEqual(
            not os.path.exists(self.filename),
            (self.option_value.lower() in options.TRUE_VALUES or
             self.env_value is not None))


_changelog_content = """7780758\x00Break parser\x00 (tag: refs/tags/1_foo.1)
04316fe\x00Make python\x00 (refs/heads/review/monty_taylor/27519)
378261a\x00Add an integration test script.\x00
3c373ac\x00Merge "Lib\x00 (HEAD, tag: refs/tags/2013.2.rc2, tag: refs/tags/2013.2, refs/heads/mile-proposed)
182feb3\x00Fix pip invocation for old versions of pip.\x00 (tag: refs/tags/0.5.17)
fa4f46e\x00Remove explicit depend on distribute.\x00 (tag: refs/tags/0.5.16)
d1c53dd\x00Use pip instead of easy_install for installation.\x00
a793ea1\x00Merge "Skip git-checkout related tests when .git is missing"\x00
6c27ce7\x00Skip git-checkout related tests when .git is missing\x00
451e513\x00Bug fix: create_stack() fails when waiting\x00
4c8cfe4\x00Improve test coverage: network delete API\x00 (tag: refs/tags/(evil))
d7e6167\x00Bug fix: Fix pass thru filtering in list_networks\x00 (tag: refs/tags/ev()il)
c47ec15\x00Consider 'in-use' a non-pending volume for caching\x00 (tag: refs/tags/ev)il)
8696fbd\x00Improve test coverage: private extension API\x00 (tag: refs/tags/ev(il)
f0440f8\x00Improve test coverage: hypervisor list\x00 (tag: refs/tags/e(vi)l)
04984a5\x00Refactor hooks file.\x00 (HEAD, tag: 0.6.7,b, tag: refs/tags/(12), refs/heads/master)
a65e8ee\x00Remove jinja pin.\x00 (tag: refs/tags/0.5.14, tag: refs/tags/0.5.13)
"""  # noqa


def _make_old_git_changelog_format(line):
    """Convert post-1.8.1 git log format to pre-1.8.1 git log format"""

    if not line.strip():
        return line
    sha, msg, refname = line.split('\x00')
    refname = refname.replace('tag: ', '')
    return '\x00'.join((sha, msg, refname))


_old_git_changelog_content = '\n'.join(
    _make_old_git_changelog_format(line)
    for line in _changelog_content.split('\n'))


class GitLogsTest(base.BaseTestCase):

    scenarios = [
        ('pre1.8.3', {'changelog': _old_git_changelog_content}),
        ('post1.8.3', {'changelog': _changelog_content}),
    ]

    def setUp(self):
        super(GitLogsTest, self).setUp()
        self.temp_path = self.useFixture(fixtures.TempDir()).path
        self.root_dir = os.path.abspath(os.path.curdir)
        self.git_dir = os.path.join(self.root_dir, ".git")
        self.useFixture(
            fixtures.EnvironmentVariable('SKIP_GENERATE_AUTHORS'))
        self.useFixture(
            fixtures.EnvironmentVariable('SKIP_WRITE_GIT_CHANGELOG'))

    def test_write_git_changelog(self):
        self.useFixture(fixtures.FakePopen(lambda _: {
            "stdout": BytesIO(self.changelog.encode('utf-8'))
        }))

        git.write_git_changelog(git_dir=self.git_dir,
                                dest_dir=self.temp_path)

        with open(os.path.join(self.temp_path, "ChangeLog"), "r") as ch_fh:
            changelog_contents = ch_fh.read()
            self.assertIn("2013.2", changelog_contents)
            self.assertIn("0.5.17", changelog_contents)
            self.assertIn("------", changelog_contents)
            self.assertIn("Refactor hooks file", changelog_contents)
            self.assertIn(
                r"Bug fix: create\_stack() fails when waiting",
                changelog_contents)
            self.assertNotIn("Refactor hooks file.", changelog_contents)
            self.assertNotIn("182feb3", changelog_contents)
            self.assertNotIn("review/monty_taylor/27519", changelog_contents)
            self.assertNotIn("0.5.13", changelog_contents)
            self.assertNotIn("0.6.7", changelog_contents)
            self.assertNotIn("12", changelog_contents)
            self.assertNotIn("(evil)", changelog_contents)
            self.assertNotIn("ev()il", changelog_contents)
            self.assertNotIn("ev(il", changelog_contents)
            self.assertNotIn("ev)il", changelog_contents)
            self.assertNotIn("e(vi)l", changelog_contents)
            self.assertNotIn('Merge "', changelog_contents)
            self.assertNotIn(r'1\_foo.1', changelog_contents)

    def test_generate_authors(self):
        author_old = u"Foo Foo <email@foo.com>"
        author_new = u"Bar Bar <email@bar.com>"
        co_author = u"Foo Bar <foo@bar.com>"
        co_author_by = u"Co-authored-by: " + co_author

        git_log_cmd = (
            "git --git-dir=%s log --format=%%aN <%%aE>"
            % self.git_dir)
        git_co_log_cmd = ("git --git-dir=%s log" % self.git_dir)
        git_top_level = "git rev-parse --show-toplevel"
        cmd_map = {
            git_log_cmd: author_new,
            git_co_log_cmd: co_author_by,
            git_top_level: self.root_dir,
        }

        exist_files = [self.git_dir,
                       os.path.join(self.temp_path, "AUTHORS.in")]
        self.useFixture(fixtures.MonkeyPatch(
            "os.path.exists",
            lambda path: os.path.abspath(path) in exist_files))

        def _fake_run_shell_command(cmd, **kwargs):
            return cmd_map[" ".join(cmd)]

        self.useFixture(fixtures.MonkeyPatch(
            "pbr.git._run_shell_command",
            _fake_run_shell_command))

        with open(os.path.join(self.temp_path, "AUTHORS.in"), "w") as auth_fh:
            auth_fh.write("%s\n" % author_old)

        git.generate_authors(git_dir=self.git_dir,
                             dest_dir=self.temp_path)

        with open(os.path.join(self.temp_path, "AUTHORS"), "r") as auth_fh:
            authors = auth_fh.read()
            self.assertIn(author_old, authors)
            self.assertIn(author_new, authors)
            self.assertIn(co_author, authors)
