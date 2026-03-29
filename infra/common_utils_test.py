# Copyright 2025 Google LLC
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
"""Tests for common_utils module."""

import os
import subprocess
import tempfile
import unittest
from unittest import mock

import common_utils
import constants


class GetProjectBuildSubdirTest(unittest.TestCase):
  """Tests for get_project_build_subdir function."""

  def test_get_project_build_subdir_creates_directory(self):
    """Tests that get_project_build_subdir creates the directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      with mock.patch.object(common_utils, 'BUILD_DIR', tmp_dir):
        result = common_utils.get_project_build_subdir('test-project', 'out')
        expected = os.path.join(tmp_dir, 'out', 'test-project')
        self.assertEqual(result, expected)
        self.assertTrue(os.path.exists(result))
        self.assertTrue(os.path.isdir(result))

  def test_get_project_build_subdir_idempotent(self):
    """Tests that calling twice doesn't fail if directory exists."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      with mock.patch.object(common_utils, 'BUILD_DIR', tmp_dir):
        result1 = common_utils.get_project_build_subdir('test-project', 'out')
        result2 = common_utils.get_project_build_subdir('test-project', 'out')
        self.assertEqual(result1, result2)
        self.assertTrue(os.path.exists(result1))

  def test_get_project_build_subdir_different_subdirs(self):
    """Tests creating different subdirectories for the same project."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      with mock.patch.object(common_utils, 'BUILD_DIR', tmp_dir):
        out_dir = common_utils.get_project_build_subdir('test-project', 'out')
        work_dir = common_utils.get_project_build_subdir('test-project', 'work')
        corpus_dir = common_utils.get_project_build_subdir('test-project',
                                                            'corpus')

        self.assertNotEqual(out_dir, work_dir)
        self.assertNotEqual(out_dir, corpus_dir)
        self.assertNotEqual(work_dir, corpus_dir)
        self.assertTrue(os.path.exists(out_dir))
        self.assertTrue(os.path.exists(work_dir))
        self.assertTrue(os.path.exists(corpus_dir))


class GetOutDirTest(unittest.TestCase):
  """Tests for get_out_dir function."""

  def test_get_out_dir_with_project(self):
    """Tests get_out_dir with a project name."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      with mock.patch.object(common_utils, 'BUILD_DIR', tmp_dir):
        result = common_utils.get_out_dir('test-project')
        expected = os.path.join(tmp_dir, 'out', 'test-project')
        self.assertEqual(result, expected)
        self.assertTrue(os.path.exists(result))

  def test_get_out_dir_without_project(self):
    """Tests get_out_dir without a project name."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      with mock.patch.object(common_utils, 'BUILD_DIR', tmp_dir):
        result = common_utils.get_out_dir()
        expected = os.path.join(tmp_dir, 'out', '')
        self.assertEqual(result, expected)


class ProjectTest(unittest.TestCase):
  """Tests for Project class."""

  def test_project_internal_initialization(self):
    """Tests Project initialization for internal OSS-Fuzz project."""
    with mock.patch.object(common_utils,
                           'OSS_FUZZ_DIR',
                           '/fake/oss-fuzz-dir'):
      project = common_utils.Project('example')
      self.assertEqual(project.name, 'example')
      self.assertEqual(project.path, '/fake/oss-fuzz-dir/projects/example')
      self.assertEqual(project.build_integration_path,
                       '/fake/oss-fuzz-dir/projects/example')
      self.assertFalse(project.is_external)

  def test_project_external_initialization(self):
    """Tests Project initialization for external project."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      project_path = os.path.join(tmp_dir, 'my-project')
      os.makedirs(project_path)

      project = common_utils.Project(project_path, is_external=True)
      self.assertEqual(project.name, 'my-project')
      self.assertEqual(project.path, project_path)
      self.assertEqual(project.build_integration_path,
                       os.path.join(project_path, '.clusterfuzzlite'))
      self.assertTrue(project.is_external)

  def test_project_external_custom_build_integration_path(self):
    """Tests external project with custom build integration path."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      project_path = os.path.join(tmp_dir, 'my-project')
      os.makedirs(project_path)

      project = common_utils.Project(project_path,
                                      is_external=True,
                                      build_integration_path='custom/path')
      self.assertEqual(project.build_integration_path,
                       os.path.join(project_path, 'custom/path'))

  def test_project_dockerfile_path(self):
    """Tests Project.dockerfile_path property."""
    with mock.patch.object(common_utils,
                           'OSS_FUZZ_DIR',
                           '/fake/oss-fuzz-dir'):
      project = common_utils.Project('example')
      expected = '/fake/oss-fuzz-dir/projects/example/Dockerfile'
      self.assertEqual(project.dockerfile_path, expected)

  def test_project_language_from_yaml(self):
    """Tests Project.language property reads from project.yaml."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      project_path = os.path.join(tmp_dir, 'test-project')
      os.makedirs(project_path)

      yaml_content = """
      language: python
      main_repo: https://github.com/example/repo
      """
      yaml_path = os.path.join(project_path, 'project.yaml')
      with open(yaml_path, 'w') as f:
        f.write(yaml_content)

      with mock.patch.object(common_utils,
                             'OSS_FUZZ_DIR',
                             '/fake/oss-fuzz-dir'):
        project = common_utils.Project('test-project')
        project.build_integration_path = project_path

        self.assertEqual(project.language, 'python')

  def test_project_language_default_when_no_yaml(self):
    """Tests Project.language returns default when project.yaml missing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      project_path = os.path.join(tmp_dir, 'test-project')
      os.makedirs(project_path)

      with mock.patch.object(common_utils,
                             'OSS_FUZZ_DIR',
                             '/fake/oss-fuzz-dir'):
        project = common_utils.Project('test-project')
        project.build_integration_path = project_path

        self.assertEqual(project.language, constants.DEFAULT_LANGUAGE)

  def test_project_language_default_when_not_specified(self):
    """Tests Project.language returns default when language not in yaml."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      project_path = os.path.join(tmp_dir, 'test-project')
      os.makedirs(project_path)

      yaml_content = """
      main_repo: https://github.com/example/repo
      """
      yaml_path = os.path.join(project_path, 'project.yaml')
      with open(yaml_path, 'w') as f:
        f.write(yaml_content)

      with mock.patch.object(common_utils,
                             'OSS_FUZZ_DIR',
                             '/fake/oss-fuzz-dir'):
        project = common_utils.Project('test-project')
        project.build_integration_path = project_path

        self.assertEqual(project.language, constants.DEFAULT_LANGUAGE)

  def test_project_base_os_version_from_yaml(self):
    """Tests Project.base_os_version property reads from project.yaml."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      project_path = os.path.join(tmp_dir, 'test-project')
      os.makedirs(project_path)

      yaml_content = """
      language: c++
      base_os_version: ubuntu-24-04
      """
      yaml_path = os.path.join(project_path, 'project.yaml')
      with open(yaml_path, 'w') as f:
        f.write(yaml_content)

      with mock.patch.object(common_utils,
                             'OSS_FUZZ_DIR',
                             '/fake/oss-fuzz-dir'):
        project = common_utils.Project('test-project')
        project.build_integration_path = project_path

        self.assertEqual(project.base_os_version, 'ubuntu-24-04')

  def test_project_base_os_version_default(self):
    """Tests Project.base_os_version returns legacy by default."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      project_path = os.path.join(tmp_dir, 'test-project')
      os.makedirs(project_path)

      with mock.patch.object(common_utils,
                             'OSS_FUZZ_DIR',
                             '/fake/oss-fuzz-dir'):
        project = common_utils.Project('test-project')
        project.build_integration_path = project_path

        self.assertEqual(project.base_os_version, 'legacy')

  def test_project_coverage_extra_args_from_yaml(self):
    """Tests Project.coverage_extra_args reads from project.yaml."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      project_path = os.path.join(tmp_dir, 'test-project')
      os.makedirs(project_path)

      yaml_content = """
language: c++
coverage_extra_args: >
  --flag1
  --flag2=value
main_repo: https://github.com/example/repo
"""
      yaml_path = os.path.join(project_path, 'project.yaml')
      with open(yaml_path, 'w') as f:
        f.write(yaml_content)

      with mock.patch.object(common_utils,
                             'OSS_FUZZ_DIR',
                             '/fake/oss-fuzz-dir'):
        project = common_utils.Project('test-project')
        project.build_integration_path = project_path

        coverage_args = project.coverage_extra_args
        self.assertIn('--flag1', coverage_args)
        self.assertIn('--flag2=value', coverage_args)

  def test_project_coverage_extra_args_empty(self):
    """Tests Project.coverage_extra_args returns empty when not specified."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      project_path = os.path.join(tmp_dir, 'test-project')
      os.makedirs(project_path)

      yaml_content = """
      language: c++
      """
      yaml_path = os.path.join(project_path, 'project.yaml')
      with open(yaml_path, 'w') as f:
        f.write(yaml_content)

      with mock.patch.object(common_utils,
                             'OSS_FUZZ_DIR',
                             '/fake/oss-fuzz-dir'):
        project = common_utils.Project('test-project')
        project.build_integration_path = project_path

        self.assertEqual(project.coverage_extra_args, '')

  def test_project_out_property(self):
    """Tests Project.out property creates and returns out directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      with mock.patch.object(common_utils, 'BUILD_DIR', tmp_dir):
        project = common_utils.Project('test-project')
        out_dir = project.out

        expected = os.path.join(tmp_dir, 'out', 'test-project')
        self.assertEqual(out_dir, expected)
        self.assertTrue(os.path.exists(out_dir))

  def test_project_work_property(self):
    """Tests Project.work property creates and returns work directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      with mock.patch.object(common_utils, 'BUILD_DIR', tmp_dir):
        project = common_utils.Project('test-project')
        work_dir = project.work

        expected = os.path.join(tmp_dir, 'work', 'test-project')
        self.assertEqual(work_dir, expected)
        self.assertTrue(os.path.exists(work_dir))

  def test_project_corpus_property(self):
    """Tests Project.corpus property creates and returns corpus directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      with mock.patch.object(common_utils, 'BUILD_DIR', tmp_dir):
        project = common_utils.Project('test-project')
        corpus_dir = project.corpus

        expected = os.path.join(tmp_dir, 'corpus', 'test-project')
        self.assertEqual(corpus_dir, expected)
        self.assertTrue(os.path.exists(corpus_dir))


class IsBaseImageTest(unittest.TestCase):
  """Tests for is_base_image function."""

  def test_is_base_image_exists(self):
    """Tests is_base_image returns True for existing base image."""
    # base-runner is a real base image in the repository
    with mock.patch('os.path.exists', return_value=True):
      result = common_utils.is_base_image('base-runner')
      self.assertTrue(result)

  def test_is_base_image_not_exists(self):
    """Tests is_base_image returns False for non-existent image."""
    with mock.patch('os.path.exists', return_value=False):
      result = common_utils.is_base_image('nonexistent-image')
      self.assertFalse(result)


class CheckProjectExistsTest(unittest.TestCase):
  """Tests for check_project_exists function."""

  def test_check_project_exists_internal(self):
    """Tests check_project_exists with an internal project that exists."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      project_path = os.path.join(tmp_dir, 'projects', 'test-project')
      os.makedirs(project_path)

      with mock.patch.object(common_utils, 'OSS_FUZZ_DIR', tmp_dir):
        project = common_utils.Project('test-project')
        result = common_utils.check_project_exists(project)
        self.assertTrue(result)

  def test_check_project_exists_internal_missing(self):
    """Tests check_project_exists with missing internal project."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      with mock.patch.object(common_utils, 'OSS_FUZZ_DIR', tmp_dir):
        project = common_utils.Project('nonexistent')
        result = common_utils.check_project_exists(project)
        self.assertFalse(result)

  def test_check_project_exists_external(self):
    """Tests check_project_exists with an external project that exists."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      project_path = os.path.join(tmp_dir, 'external-project')
      os.makedirs(project_path)

      project = common_utils.Project(project_path, is_external=True)
      result = common_utils.check_project_exists(project)
      self.assertTrue(result)

  def test_check_project_exists_external_missing(self):
    """Tests check_project_exists with missing external project."""
    project = common_utils.Project('/nonexistent/path', is_external=True)
    result = common_utils.check_project_exists(project)
    self.assertFalse(result)


class GetCommandStringTest(unittest.TestCase):
  """Tests for get_command_string function."""

  def test_get_command_string_simple(self):
    """Tests get_command_string with simple commands."""
    command = ['docker', 'build', '-t', 'image:tag']
    result = common_utils.get_command_string(command)
    self.assertEqual(result, 'docker build -t image:tag')

  def test_get_command_string_with_spaces(self):
    """Tests get_command_string properly escapes arguments with spaces."""
    command = ['echo', 'hello world', 'test']
    result = common_utils.get_command_string(command)
    # shlex.quote should quote the argument with space
    self.assertIn("'hello world'", result)

  def test_get_command_string_with_special_chars(self):
    """Tests get_command_string with special characters."""
    command = ['sh', '-c', 'echo $PATH']
    result = common_utils.get_command_string(command)
    # Special characters should be properly escaped
    self.assertIn('sh', result)
    self.assertIn('-c', result)


class DockerBuildTest(unittest.TestCase):
  """Tests for docker_build function."""

  @mock.patch('subprocess.check_call')
  def test_docker_build_success(self, mock_check_call):
    """Tests docker_build with successful build."""
    build_args = ['-t', 'test:tag', '.']
    result = common_utils.docker_build(build_args)

    self.assertTrue(result)
    mock_check_call.assert_called_once_with(['docker', 'build', '-t', 'test:tag', '.'])

  @mock.patch('subprocess.check_call')
  def test_docker_build_failure(self, mock_check_call):
    """Tests docker_build with failed build."""
    mock_check_call.side_effect = subprocess.CalledProcessError(1, 'docker')

    build_args = ['-t', 'test:tag', '.']
    result = common_utils.docker_build(build_args)

    self.assertFalse(result)


class DockerPullTest(unittest.TestCase):
  """Tests for docker_pull function."""

  @mock.patch('subprocess.check_call')
  def test_docker_pull_success(self, mock_check_call):
    """Tests docker_pull with successful pull."""
    result = common_utils.docker_pull('gcr.io/test/image:tag')

    self.assertTrue(result)
    mock_check_call.assert_called_once_with(['docker', 'pull',
                                             'gcr.io/test/image:tag'])

  @mock.patch('subprocess.check_call')
  def test_docker_pull_failure(self, mock_check_call):
    """Tests docker_pull with failed pull."""
    mock_check_call.side_effect = subprocess.CalledProcessError(1, 'docker')

    result = common_utils.docker_pull('gcr.io/test/image:tag')

    self.assertFalse(result)


class PullImagesTest(unittest.TestCase):
  """Tests for pull_images function."""

  @mock.patch('common_utils.docker_pull')
  def test_pull_images_all_languages(self, mock_docker_pull):
    """Tests pull_images pulls all base images when no language specified."""
    mock_docker_pull.return_value = True

    result = common_utils.pull_images()

    self.assertTrue(result)
    # Should pull generic images plus all language-specific images
    self.assertGreater(mock_docker_pull.call_count, 5)

  @mock.patch('common_utils.docker_pull')
  def test_pull_images_specific_language(self, mock_docker_pull):
    """Tests pull_images pulls only generic and specified language images."""
    mock_docker_pull.return_value = True

    result = common_utils.pull_images(language='python')

    self.assertTrue(result)
    # Check that python image was pulled
    calls = [call[0][0] for call in mock_docker_pull.call_args_list]
    self.assertIn('gcr.io/oss-fuzz-base/base-builder-python', calls)
    # Generic images should also be pulled
    self.assertIn('gcr.io/oss-fuzz-base/base-builder', calls)

  @mock.patch('common_utils.docker_pull')
  def test_pull_images_failure(self, mock_docker_pull):
    """Tests pull_images returns False on first failure."""
    mock_docker_pull.return_value = False

    result = common_utils.pull_images()

    self.assertFalse(result)


class BuildImageImplTest(unittest.TestCase):
  """Tests for build_image_impl function."""

  @mock.patch('common_utils.docker_build')
  @mock.patch('common_utils.check_project_exists')
  @mock.patch('common_utils.is_base_image')
  def test_build_image_impl_regular_project(self, mock_is_base, mock_check,
                                             mock_docker_build):
    """Tests build_image_impl for a regular project."""
    mock_is_base.return_value = False
    mock_check.return_value = True
    mock_docker_build.return_value = True

    with tempfile.TemporaryDirectory() as tmp_dir:
      project_path = os.path.join(tmp_dir, 'projects', 'test-project')
      os.makedirs(project_path)

      with mock.patch.object(common_utils, 'OSS_FUZZ_DIR', tmp_dir):
        project = common_utils.Project('test-project')
        result = common_utils.build_image_impl(project, cache=True, pull=False)

        self.assertTrue(result)
        mock_docker_build.assert_called_once()

  @mock.patch('common_utils.docker_build')
  @mock.patch('common_utils.check_project_exists')
  @mock.patch('common_utils.is_base_image', return_value=False)
  def test_build_image_impl_project_not_exists(self, mock_is_base, mock_check,
                                                 mock_docker_build):
    """Tests build_image_impl returns False when project doesn't exist."""
    mock_check.return_value = False

    project = common_utils.Project('nonexistent')
    result = common_utils.build_image_impl(project)

    self.assertFalse(result)
    mock_docker_build.assert_not_called()

  @mock.patch('subprocess.check_call')
  @mock.patch('common_utils.is_base_image')
  def test_build_image_impl_base_image(self, mock_is_base, mock_check_call):
    """Tests build_image_impl for a base image."""
    mock_is_base.return_value = True
    mock_check_call.return_value = 0

    with tempfile.TemporaryDirectory() as tmp_dir:
      base_image_dir = os.path.join(tmp_dir, 'infra', 'base-images',
                                     'base-runner')
      os.makedirs(base_image_dir)
      dockerfile_path = os.path.join(base_image_dir, 'Dockerfile')
      with open(dockerfile_path, 'w') as f:
        f.write('FROM ubuntu\n')

      with mock.patch.object(common_utils, 'OSS_FUZZ_DIR', tmp_dir):
        project = common_utils.Project('base-runner')
        result = common_utils.build_image_impl(project)

        # For base images, docker_build should be called
        self.assertTrue(result)

  @mock.patch('common_utils.pull_images')
  @mock.patch('common_utils.docker_build')
  @mock.patch('common_utils.check_project_exists')
  @mock.patch('common_utils.is_base_image')
  def test_build_image_impl_with_pull(self, mock_is_base, mock_check,
                                        mock_docker_build, mock_pull_images):
    """Tests build_image_impl with pull=True."""
    mock_is_base.return_value = False
    mock_check.return_value = True
    mock_pull_images.return_value = True
    mock_docker_build.return_value = True

    with tempfile.TemporaryDirectory() as tmp_dir:
      project_path = os.path.join(tmp_dir, 'projects', 'test-project')
      os.makedirs(project_path)

      with mock.patch.object(common_utils, 'OSS_FUZZ_DIR', tmp_dir):
        project = common_utils.Project('test-project')
        result = common_utils.build_image_impl(project, pull=True)

        self.assertTrue(result)
        mock_pull_images.assert_called_once()

  @mock.patch('subprocess.check_call')
  @mock.patch('common_utils.check_project_exists')
  @mock.patch('common_utils.is_base_image')
  def test_build_image_impl_aarch64(self, mock_is_base, mock_check,
                                     mock_check_call):
    """Tests build_image_impl with aarch64 architecture."""
    mock_is_base.return_value = False
    mock_check.return_value = True
    mock_check_call.return_value = 0

    with tempfile.TemporaryDirectory() as tmp_dir:
      project_path = os.path.join(tmp_dir, 'projects', 'test-project')
      os.makedirs(project_path)

      with mock.patch.object(common_utils, 'OSS_FUZZ_DIR', tmp_dir):
        project = common_utils.Project('test-project')
        result = common_utils.build_image_impl(project,
                                                 architecture='aarch64')

        self.assertTrue(result)
        # Verify buildx was used
        call_args = mock_check_call.call_args[0][0]
        self.assertIn('buildx', call_args)
        self.assertIn('linux/arm64', call_args)


if __name__ == '__main__':
  unittest.main()
