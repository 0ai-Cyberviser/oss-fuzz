# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for workspace_utils.py"""
import os
import unittest

import workspace_utils
import test_helpers


class WorkspaceTest(unittest.TestCase):
  """Tests for the Workspace class."""

  def setUp(self):
    self.workspace_path = '/my/workspace'
    self.workspace = test_helpers.create_workspace(self.workspace_path)

  def test_workspace_attribute(self):
    """Tests that the workspace attribute is set correctly."""
    self.assertEqual(self.workspace.workspace, self.workspace_path)

  def test_repo_storage(self):
    """Tests that repo_storage returns the correct path."""
    expected = os.path.join(self.workspace_path, 'storage')
    self.assertEqual(self.workspace.repo_storage, expected)

  def test_out(self):
    """Tests that out returns the correct path."""
    expected = os.path.join(self.workspace_path, 'build-out')
    self.assertEqual(self.workspace.out, expected)

  def test_work(self):
    """Tests that work returns the correct path."""
    expected = os.path.join(self.workspace_path, 'work')
    self.assertEqual(self.workspace.work, expected)

  def test_artifacts(self):
    """Tests that artifacts returns the correct path."""
    expected = os.path.join(self.workspace_path, 'out', 'artifacts')
    self.assertEqual(self.workspace.artifacts, expected)

  def test_clusterfuzz_build(self):
    """Tests that clusterfuzz_build returns the correct path."""
    expected = os.path.join(self.workspace_path, 'cifuzz-prev-build')
    self.assertEqual(self.workspace.clusterfuzz_build, expected)

  def test_clusterfuzz_coverage(self):
    """Tests that clusterfuzz_coverage returns the correct path."""
    expected = os.path.join(self.workspace_path, 'cifuzz-prev-coverage')
    self.assertEqual(self.workspace.clusterfuzz_coverage, expected)

  def test_coverage_report(self):
    """Tests that coverage_report returns the correct path."""
    expected = os.path.join(self.workspace_path, 'cifuzz-coverage')
    self.assertEqual(self.workspace.coverage_report, expected)

  def test_corpora(self):
    """Tests that corpora returns the correct path."""
    expected = os.path.join(self.workspace_path, 'cifuzz-corpus')
    self.assertEqual(self.workspace.corpora, expected)

  def test_pruned_corpora(self):
    """Tests that pruned_corpora returns the correct path."""
    expected = os.path.join(self.workspace_path, 'cifuzz-pruned-corpus')
    self.assertEqual(self.workspace.pruned_corpora, expected)

  def test_sarif(self):
    """Tests that sarif returns the correct path."""
    expected = os.path.join(self.workspace_path, 'cifuzz-sarif')
    self.assertEqual(self.workspace.sarif, expected)

  def test_initialize_dir_creates_directory(self):
    """Tests that initialize_dir creates a directory if it doesn't exist."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
      new_dir = os.path.join(tmp_dir, 'new_subdir')
      self.assertFalse(os.path.exists(new_dir))
      self.workspace.initialize_dir(new_dir)
      self.assertTrue(os.path.isdir(new_dir))

  def test_initialize_dir_existing_directory(self):
    """Tests that initialize_dir doesn't fail if directory already exists."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
      # Should not raise even if directory exists.
      self.workspace.initialize_dir(tmp_dir)
      self.assertTrue(os.path.isdir(tmp_dir))

  def test_all_paths_under_workspace(self):
    """Tests that all path properties are under the workspace directory."""
    properties = [
        self.workspace.repo_storage,
        self.workspace.out,
        self.workspace.work,
        self.workspace.artifacts,
        self.workspace.clusterfuzz_build,
        self.workspace.clusterfuzz_coverage,
        self.workspace.coverage_report,
        self.workspace.corpora,
        self.workspace.pruned_corpora,
        self.workspace.sarif,
    ]
    for path in properties:
      self.assertTrue(
          path.startswith(self.workspace_path),
          f'{path} does not start with workspace path {self.workspace_path}')


if __name__ == '__main__':
  unittest.main()
