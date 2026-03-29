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
"""Tests for filestore/filesystem."""
import os
import sys
import tempfile
import unittest
from unittest import mock

# pylint: disable=wrong-import-position
INFRA_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))))
sys.path.append(INFRA_DIR)

from filestore import filesystem
import test_helpers

# pylint: disable=protected-access


class RecursiveListDirTest(unittest.TestCase):
  """Tests for recursive_list_dir."""

  def test_empty_directory(self):
    """Tests that an empty directory returns an empty list."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      result = filesystem.recursive_list_dir(tmp_dir)
      self.assertEqual(result, [])

  def test_flat_directory(self):
    """Tests that files in a flat directory are listed."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      file1 = os.path.join(tmp_dir, 'file1.txt')
      file2 = os.path.join(tmp_dir, 'file2.txt')
      open(file1, 'w').close()
      open(file2, 'w').close()
      result = filesystem.recursive_list_dir(tmp_dir)
      self.assertCountEqual(result, [file1, file2])

  def test_nested_directory(self):
    """Tests that files in nested subdirectories are listed."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      subdir = os.path.join(tmp_dir, 'subdir')
      os.makedirs(subdir)
      file1 = os.path.join(tmp_dir, 'top_file.txt')
      file2 = os.path.join(subdir, 'nested_file.txt')
      open(file1, 'w').close()
      open(file2, 'w').close()
      result = filesystem.recursive_list_dir(tmp_dir)
      self.assertCountEqual(result, [file1, file2])

  def test_only_returns_files_not_dirs(self):
    """Tests that only files, not directories, are returned."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      subdir = os.path.join(tmp_dir, 'subdir')
      os.makedirs(subdir)
      result = filesystem.recursive_list_dir(tmp_dir)
      # The subdir itself should not be in the list.
      self.assertNotIn(subdir, result)


class FilesystemFilestoreTest(unittest.TestCase):
  """Tests for FilesystemFilestore."""

  def setUp(self):
    self.filestore_root = tempfile.TemporaryDirectory()
    self.addCleanup(self.filestore_root.cleanup)
    self.src_dir = tempfile.TemporaryDirectory()
    self.addCleanup(self.src_dir.cleanup)
    self.dst_dir = tempfile.TemporaryDirectory()
    self.addCleanup(self.dst_dir.cleanup)

    # Create a mock config that supplies the filestore root directory.
    mock_platform_conf = mock.MagicMock()
    mock_platform_conf.filestore_root_dir = self.filestore_root.name
    config = test_helpers.create_run_config(workspace='/workspace')
    config.platform_conf = mock_platform_conf
    self.filestore = filesystem.FilesystemFilestore(config)

  def _create_test_file(self, directory, name, content='test'):
    """Creates a test file in |directory| with the given |name|."""
    path = os.path.join(directory, name)
    with open(path, 'w') as f:
      f.write(content)
    return path

  def test_upload_build(self):
    """Tests that upload_build copies files to the filestore."""
    self._create_test_file(self.src_dir.name, 'fuzzer_binary')
    self.filestore.upload_build('my-build', self.src_dir.name)
    expected_dest = os.path.join(self.filestore_root.name,
                                 filesystem.FilesystemFilestore.BUILD_DIR,
                                 'my-build', 'fuzzer_binary')
    self.assertTrue(os.path.exists(expected_dest))

  def test_download_build(self):
    """Tests that download_build retrieves files from the filestore."""
    # Pre-populate the filestore.
    build_dir = os.path.join(self.filestore_root.name,
                             filesystem.FilesystemFilestore.BUILD_DIR,
                             'my-build')
    os.makedirs(build_dir)
    self._create_test_file(build_dir, 'fuzzer_binary')
    self.filestore.download_build('my-build', self.dst_dir.name)
    self.assertTrue(
        os.path.exists(os.path.join(self.dst_dir.name, 'fuzzer_binary')))

  def test_upload_corpus(self):
    """Tests that upload_corpus copies corpus files to the filestore."""
    self._create_test_file(self.src_dir.name, 'seed1')
    self.filestore.upload_corpus('my-fuzzer', self.src_dir.name)
    expected_dest = os.path.join(self.filestore_root.name,
                                 filesystem.FilesystemFilestore.CORPUS_DIR,
                                 'my-fuzzer', 'seed1')
    self.assertTrue(os.path.exists(expected_dest))

  def test_download_corpus(self):
    """Tests that download_corpus retrieves corpus files from the filestore."""
    corpus_dir = os.path.join(self.filestore_root.name,
                              filesystem.FilesystemFilestore.CORPUS_DIR,
                              'my-fuzzer')
    os.makedirs(corpus_dir)
    self._create_test_file(corpus_dir, 'seed1')
    self.filestore.download_corpus('my-fuzzer', self.dst_dir.name)
    self.assertTrue(os.path.exists(os.path.join(self.dst_dir.name, 'seed1')))

  def test_upload_crashes(self):
    """Tests that upload_crashes copies crash files to the filestore."""
    self._create_test_file(self.src_dir.name, 'crash-abc123')
    self.filestore.upload_crashes('current', self.src_dir.name)
    expected_dest = os.path.join(self.filestore_root.name,
                                 filesystem.FilesystemFilestore.CRASHES_DIR,
                                 'current', 'crash-abc123')
    self.assertTrue(os.path.exists(expected_dest))

  def test_upload_coverage(self):
    """Tests that upload_coverage copies coverage report to the filestore."""
    self._create_test_file(self.src_dir.name, 'summary.json')
    self.filestore.upload_coverage('my-project', self.src_dir.name)
    expected_dest = os.path.join(self.filestore_root.name,
                                 filesystem.FilesystemFilestore.COVERAGE_DIR,
                                 'my-project', 'summary.json')
    self.assertTrue(os.path.exists(expected_dest))

  def test_download_coverage(self):
    """Tests that download_coverage retrieves coverage report from filestore."""
    coverage_dir = os.path.join(self.filestore_root.name,
                                filesystem.FilesystemFilestore.COVERAGE_DIR,
                                'my-project')
    os.makedirs(coverage_dir)
    self._create_test_file(coverage_dir, 'summary.json')
    self.filestore.download_coverage('my-project', self.dst_dir.name)
    self.assertTrue(
        os.path.exists(os.path.join(self.dst_dir.name, 'summary.json')))

  def test_upload_corpus_replace(self):
    """Tests that upload_corpus with replace=True deletes old files."""
    # Pre-populate the filestore with an old file.
    corpus_dir = os.path.join(self.filestore_root.name,
                              filesystem.FilesystemFilestore.CORPUS_DIR,
                              'my-fuzzer')
    os.makedirs(corpus_dir)
    old_file = os.path.join(corpus_dir, 'old_seed')
    open(old_file, 'w').close()

    # Upload new corpus with replace=True.
    self._create_test_file(self.src_dir.name, 'new_seed')
    self.filestore.upload_corpus('my-fuzzer', self.src_dir.name, replace=True)

    # Old seed should be deleted, new seed should be present.
    self.assertFalse(os.path.exists(old_file))
    self.assertTrue(
        os.path.exists(os.path.join(corpus_dir, 'new_seed')))

  def test_upload_corpus_no_replace(self):
    """Tests that upload_corpus with replace=False keeps old files."""
    # Pre-populate the filestore with an old file.
    corpus_dir = os.path.join(self.filestore_root.name,
                              filesystem.FilesystemFilestore.CORPUS_DIR,
                              'my-fuzzer')
    os.makedirs(corpus_dir)
    old_file = os.path.join(corpus_dir, 'old_seed')
    open(old_file, 'w').close()

    # Upload new corpus without replace.
    self._create_test_file(self.src_dir.name, 'new_seed')
    self.filestore.upload_corpus('my-fuzzer', self.src_dir.name, replace=False)

    # Both old and new seed should be present.
    self.assertTrue(os.path.exists(old_file))
    self.assertTrue(
        os.path.exists(os.path.join(corpus_dir, 'new_seed')))


if __name__ == '__main__':
  unittest.main()
