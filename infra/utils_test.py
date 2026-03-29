# Copyright 2020 Google LLC
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
"""Tests the functionality of the utils module's functions"""

import os
import subprocess
import tempfile
import unittest
from unittest import mock

import utils
import helper

EXAMPLE_PROJECT = 'example'

TEST_OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'cifuzz', 'test_data', 'build-out')


class IsFuzzTargetLocalTest(unittest.TestCase):
  """Tests the is_fuzz_target_local function."""

  def test_invalid_filepath(self):
    """Tests the function with an invalid file path."""
    is_local = utils.is_fuzz_target_local('not/a/real/file')
    self.assertFalse(is_local)
    is_local = utils.is_fuzz_target_local('')
    self.assertFalse(is_local)
    is_local = utils.is_fuzz_target_local(' ')
    self.assertFalse(is_local)

  def test_valid_filepath(self):
    """Checks is_fuzz_target_local function with a valid filepath."""

    is_local = utils.is_fuzz_target_local(
        os.path.join(TEST_OUT_DIR, 'example_crash_fuzzer'))
    self.assertTrue(is_local)
    is_local = utils.is_fuzz_target_local(TEST_OUT_DIR)
    self.assertFalse(is_local)


class GetFuzzTargetsTest(unittest.TestCase):
  """Tests the get_fuzz_targets function."""

  def test_valid_filepath(self):
    """Tests that fuzz targets can be retrieved once the fuzzers are built."""
    fuzz_targets = utils.get_fuzz_targets(TEST_OUT_DIR)
    crash_fuzzer_path = os.path.join(TEST_OUT_DIR, 'example_crash_fuzzer')
    nocrash_fuzzer_path = os.path.join(TEST_OUT_DIR, 'example_nocrash_fuzzer')
    self.assertCountEqual(fuzz_targets,
                          [crash_fuzzer_path, nocrash_fuzzer_path])

    # Testing on a arbitrary directory with no fuzz targets in it.
    fuzz_targets = utils.get_fuzz_targets(
        os.path.join(helper.OSS_FUZZ_DIR, 'infra', 'travis'))
    self.assertFalse(fuzz_targets)

  def test_invalid_filepath(self):
    """Tests what get_fuzz_targets return when invalid filepath is used."""
    fuzz_targets = utils.get_fuzz_targets('not/a/valid/file/path')
    self.assertFalse(fuzz_targets)


class ExecuteTest(unittest.TestCase):
  """Tests the execute function."""

  def test_valid_command(self):
    """Tests that execute can produce valid output."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      out, err, err_code = utils.execute(['ls', '.'],
                                         location=tmp_dir,
                                         check_result=False)
      self.assertEqual(err_code, 0)
      self.assertEqual(err, '')
      self.assertEqual(out, '')
      out, err, err_code = utils.execute(['mkdir', 'tmp'],
                                         location=tmp_dir,
                                         check_result=False)
      self.assertEqual(err_code, 0)
      self.assertEqual(err, '')
      self.assertEqual(out, '')
      out, err, err_code = utils.execute(['ls', '.'],
                                         location=tmp_dir,
                                         check_result=False)
      self.assertEqual(err_code, 0)
      self.assertEqual(err, '')
      self.assertEqual(out, 'tmp\n')

  def test_error_command(self):
    """Tests that execute can correctly surface errors."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      out, err, err_code = utils.execute(['ls', 'notarealdir'],
                                         location=tmp_dir,
                                         check_result=False)
      self.assertEqual(err_code, 2)
      self.assertIsNotNone(err)
      self.assertEqual(out, '')
      with self.assertRaises(RuntimeError):
        out, err, err_code = utils.execute(['ls', 'notarealdir'],
                                           location=tmp_dir,
                                           check_result=True)


class BinaryPrintTest(unittest.TestCase):
  """Tests for utils.binary_print."""

  @unittest.skip('Causes spurious failures because of side-effects.')
  def test_string(self):  # pylint: disable=no-self-use
    """Tests that utils.binary_print can print a regular string."""
    # Should execute without raising any exceptions.
    with mock.patch('sys.stdout.buffer.write') as mock_write:
      utils.binary_print('hello')
      mock_write.assert_called_with('hello\n')

  @unittest.skip('Causes spurious failures because of side-effects.')
  def test_binary_string(self):  # pylint: disable=no-self-use
    """Tests that utils.binary_print can print a bianry string."""
    # Should execute without raising any exceptions.
    with mock.patch('sys.stdout.buffer.write') as mock_write:
      utils.binary_print(b'hello')
      mock_write.assert_called_with(b'hello\n')


class CommandToStringTest(unittest.TestCase):
  """Tests for command_to_string."""

  def test_string(self):
    """Tests that command_to_string returns the argument passed to it when it is
    passed a string."""
    command = 'command'
    self.assertEqual(utils.command_to_string(command), command)

  def test_list(self):
    """Tests that command_to_string returns the correct stringwhen it is passed
    a list."""
    command = ['command', 'arg1', 'arg2']
    self.assertEqual(utils.command_to_string(command), 'command arg1 arg2')


class ChdirToRootTest(unittest.TestCase):
  """Tests for chdir_to_root function."""

  def test_chdir_to_root_from_different_directory(self):
    """Tests that chdir_to_root changes to the OSS-Fuzz root directory."""
    original_dir = os.getcwd()
    try:
      # Change to a temporary directory
      with tempfile.TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)
        self.assertNotEqual(os.getcwd(), helper.OSS_FUZZ_DIR)

        # Call chdir_to_root
        utils.chdir_to_root()

        # Verify we're now in the OSS-Fuzz root directory
        self.assertEqual(os.getcwd(), helper.OSS_FUZZ_DIR)
    finally:
      # Restore original directory
      os.chdir(original_dir)

  def test_chdir_to_root_when_already_in_root(self):
    """Tests that chdir_to_root works correctly when already in root."""
    original_dir = os.getcwd()
    try:
      # Ensure we're in the root directory
      os.chdir(helper.OSS_FUZZ_DIR)
      utils.chdir_to_root()
      # Should still be in root directory
      self.assertEqual(os.getcwd(), helper.OSS_FUZZ_DIR)
    finally:
      os.chdir(original_dir)


class GetContainerNameTest(unittest.TestCase):
  """Tests for get_container_name function."""

  @mock.patch('subprocess.run')
  @mock.patch('builtins.open', new_callable=mock.mock_open, read_data='test-container-id\n')
  def test_get_container_name_in_docker(self, mock_open_file, mock_run):
    """Tests getting container name when running in a Docker container."""
    # Mock systemd-detect-virt to return 'docker'
    mock_run.return_value.stdout = b'docker\n'

    result = utils.get_container_name()

    self.assertEqual(result, 'test-container-id')
    mock_run.assert_called_once_with(['systemd-detect-virt', '-c'],
                                      stdout=subprocess.PIPE)
    mock_open_file.assert_called_once_with('/etc/hostname')

  @mock.patch('subprocess.run')
  def test_get_container_name_not_in_docker(self, mock_run):
    """Tests getting container name when not running in a Docker container."""
    # Mock systemd-detect-virt to return something other than 'docker'
    mock_run.return_value.stdout = b'none\n'

    result = utils.get_container_name()

    self.assertIsNone(result)
    mock_run.assert_called_once_with(['systemd-detect-virt', '-c'],
                                      stdout=subprocess.PIPE)


class IsExecutableTest(unittest.TestCase):
  """Tests for is_executable function."""

  def test_is_executable_with_executable_file(self):
    """Tests is_executable with an actual executable file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
      tmp_path = tmp_file.name
      tmp_file.write('#!/bin/bash\necho hello')

    try:
      # Make file executable
      os.chmod(tmp_path, 0o755)
      self.assertTrue(utils.is_executable(tmp_path))
    finally:
      os.unlink(tmp_path)

  def test_is_executable_with_non_executable_file(self):
    """Tests is_executable with a non-executable file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
      tmp_path = tmp_file.name
      tmp_file.write('not executable')

    try:
      # Make file non-executable
      os.chmod(tmp_path, 0o644)
      self.assertFalse(utils.is_executable(tmp_path))
    finally:
      os.unlink(tmp_path)

  def test_is_executable_with_nonexistent_file(self):
    """Tests is_executable with a nonexistent file path."""
    self.assertFalse(utils.is_executable('/nonexistent/file/path'))


class UrlJoinTest(unittest.TestCase):
  """Tests for url_join function."""

  def test_url_join_basic(self):
    """Tests basic URL joining."""
    result = utils.url_join('https://example.com', 'path', 'to', 'resource')
    self.assertEqual(result, 'https://example.com/path/to/resource')

  def test_url_join_with_trailing_slash(self):
    """Tests URL joining with trailing slashes."""
    result = utils.url_join('https://example.com/', 'path/')
    self.assertEqual(result, 'https://example.com/path/')

  def test_url_join_single_part(self):
    """Tests URL joining with a single part."""
    result = utils.url_join('https://example.com')
    self.assertEqual(result, 'https://example.com')

  def test_url_join_empty_parts(self):
    """Tests URL joining with empty string parts."""
    result = utils.url_join('https://example.com', '', 'path')
    # posixpath.join treats '' as current dir, so joins all parts
    self.assertEqual(result, 'https://example.com/path')

  def test_url_join_multiple_slashes(self):
    """Tests that url_join handles multiple slashes correctly."""
    result = utils.url_join('https://example.com/', '/path/', '/to/', '/file')
    # posixpath.join with absolute paths keeps only the last absolute path
    self.assertEqual(result, '/file')


class GsUrlToHttpsTest(unittest.TestCase):
  """Tests for gs_url_to_https function."""

  def test_gs_url_to_https_basic(self):
    """Tests basic conversion from gs:// to https://."""
    gs_url = 'gs://bucket-name/path/to/file'
    expected = 'https://storage.googleapis.com/bucket-name/path/to/file'
    result = utils.gs_url_to_https(gs_url)
    self.assertEqual(result, expected)

  def test_gs_url_to_https_with_subdirectories(self):
    """Tests conversion with multiple subdirectories."""
    gs_url = 'gs://my-bucket/sub1/sub2/sub3/file.txt'
    expected = 'https://storage.googleapis.com/my-bucket/sub1/sub2/sub3/file.txt'
    result = utils.gs_url_to_https(gs_url)
    self.assertEqual(result, expected)

  def test_gs_url_to_https_simple_bucket(self):
    """Tests conversion with just a bucket name."""
    gs_url = 'gs://bucket-name'
    expected = 'https://storage.googleapis.com/bucket-name'
    result = utils.gs_url_to_https(gs_url)
    self.assertEqual(result, expected)


class RemovePrefixTest(unittest.TestCase):
  """Tests for remove_prefix function."""

  def test_remove_prefix_with_matching_prefix(self):
    """Tests removing a prefix that exists."""
    result = utils.remove_prefix('gs://bucket/path', 'gs://')
    self.assertEqual(result, 'bucket/path')

  def test_remove_prefix_with_no_matching_prefix(self):
    """Tests removing a prefix that doesn't exist."""
    result = utils.remove_prefix('https://example.com', 'gs://')
    self.assertEqual(result, 'https://example.com')

  def test_remove_prefix_empty_string(self):
    """Tests remove_prefix with empty string."""
    result = utils.remove_prefix('', 'prefix')
    self.assertEqual(result, '')

  def test_remove_prefix_empty_prefix(self):
    """Tests remove_prefix with empty prefix."""
    result = utils.remove_prefix('some string', '')
    self.assertEqual(result, 'some string')

  def test_remove_prefix_partial_match(self):
    """Tests that partial matches don't remove anything."""
    result = utils.remove_prefix('abcdef', 'abcxyz')
    self.assertEqual(result, 'abcdef')

  def test_remove_prefix_entire_string(self):
    """Tests removing a prefix that is the entire string."""
    result = utils.remove_prefix('prefix', 'prefix')
    self.assertEqual(result, '')


if __name__ == '__main__':
  unittest.main()
