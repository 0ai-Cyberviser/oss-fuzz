# Copyright 2022 Google LLC
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
"""Tests for manifest module."""

import unittest
from unittest import mock

import manifest


class PushManifestTest(unittest.TestCase):
  """Tests for push_manifest function."""

  @mock.patch('subprocess.run')
  def test_push_manifest_success(self, mock_run):
    """Tests that push_manifest executes the correct docker commands."""
    mock_run.return_value.returncode = 0

    result = manifest.push_manifest('gcr.io/test/image')

    self.assertTrue(result)

    # Verify all expected docker commands were called
    expected_calls = [
        # Pull main image
        mock.call(['docker', 'pull', 'gcr.io/test/image'], check=True),
        # Tag AMD64 version
        mock.call(
            ['docker', 'tag', 'gcr.io/test/image', 'gcr.io/test/image:manifest-amd64'],
            check=True),
        # Push AMD64 version
        mock.call(['docker', 'push', 'gcr.io/test/image:manifest-amd64'], check=True),
        # Pull ARM version
        mock.call(['docker', 'pull', 'gcr.io/test/image-testing-arm'], check=True),
        # Tag ARM64 version
        mock.call([
            'docker', 'tag', 'gcr.io/test/image-testing-arm',
            'gcr.io/test/image:manifest-arm64v8'
        ],
                  check=True),
        # Create manifest
        mock.call([
            'docker', 'manifest', 'create', 'gcr.io/test/image', '--amend',
            'gcr.io/test/image:manifest-arm64v8', '--amend',
            'gcr.io/test/image:manifest-amd64'
        ],
                  check=True),
        # Push manifest
        mock.call(['docker', 'manifest', 'push', 'gcr.io/test/image'], check=True),
    ]

    self.assertEqual(mock_run.call_count, 7)
    mock_run.assert_has_calls(expected_calls, any_order=False)

  @mock.patch('subprocess.run')
  def test_push_manifest_with_different_image(self, mock_run):
    """Tests push_manifest with a different image name."""
    mock_run.return_value.returncode = 0

    result = manifest.push_manifest('gcr.io/oss-fuzz-base/base-builder')

    self.assertTrue(result)
    self.assertEqual(mock_run.call_count, 7)

    # Verify the correct ARM image name is derived
    arm_image_call = mock_run.call_args_list[3]
    self.assertIn('gcr.io/oss-fuzz-base/base-builder-testing-arm',
                  arm_image_call[0][0])

  @mock.patch('subprocess.run')
  def test_push_manifest_docker_pull_failure(self, mock_run):
    """Tests that push_manifest raises exception on docker pull failure."""
    # Make the first docker pull fail
    mock_run.side_effect = [
        Exception('Docker pull failed'),
    ]

    with self.assertRaises(Exception) as context:
      manifest.push_manifest('gcr.io/test/image')

    self.assertIn('Docker pull failed', str(context.exception))

  @mock.patch('subprocess.run')
  def test_push_manifest_docker_tag_failure(self, mock_run):
    """Tests that push_manifest raises exception on docker tag failure."""
    # Make the first tag operation fail
    mock_run.side_effect = [
        mock.Mock(returncode=0),  # pull succeeds
        Exception('Docker tag failed'),  # tag fails
    ]

    with self.assertRaises(Exception) as context:
      manifest.push_manifest('gcr.io/test/image')

    self.assertIn('Docker tag failed', str(context.exception))

  @mock.patch('subprocess.run')
  def test_push_manifest_manifest_create_failure(self, mock_run):
    """Tests that push_manifest raises exception on manifest create failure."""
    # Make manifest create fail
    mock_run.side_effect = [
        mock.Mock(returncode=0),  # pull
        mock.Mock(returncode=0),  # tag amd64
        mock.Mock(returncode=0),  # push amd64
        mock.Mock(returncode=0),  # pull arm
        mock.Mock(returncode=0),  # tag arm64
        Exception('Manifest create failed'),  # manifest create fails
    ]

    with self.assertRaises(Exception) as context:
      manifest.push_manifest('gcr.io/test/image')

    self.assertIn('Manifest create failed', str(context.exception))


class MainTest(unittest.TestCase):
  """Tests for main function."""

  @mock.patch('manifest.push_manifest')
  @mock.patch('subprocess.run')
  def test_main_success(self, mock_run, mock_push_manifest):
    """Tests that main successfully processes both images."""
    mock_run.return_value.returncode = 0
    mock_push_manifest.return_value = True

    result = manifest.main()

    self.assertEqual(result, 0)

    # Verify gcloud command was called
    mock_run.assert_called_once_with(['gcloud', 'projects', 'list', '--limit=1'],
                                      check=True)

    # Verify push_manifest was called for both images
    self.assertEqual(mock_push_manifest.call_count, 2)
    expected_images = [
        'gcr.io/oss-fuzz-base/base-builder',
        'gcr.io/oss-fuzz-base/base-runner',
    ]
    actual_images = [
        call[0][0] for call in mock_push_manifest.call_args_list
    ]
    self.assertEqual(actual_images, expected_images)

  @mock.patch('manifest.push_manifest')
  @mock.patch('subprocess.run')
  def test_main_gcloud_failure(self, mock_run, mock_push_manifest):
    """Tests that main fails when gcloud command fails."""
    mock_run.side_effect = Exception('gcloud failed')

    with self.assertRaises(Exception):
      manifest.main()

    # push_manifest should not be called if gcloud fails
    mock_push_manifest.assert_not_called()

  @mock.patch('manifest.push_manifest')
  @mock.patch('subprocess.run')
  def test_main_partial_failure(self, mock_run, mock_push_manifest):
    """Tests that main returns error code when one push fails."""
    mock_run.return_value.returncode = 0
    # First image succeeds, second fails
    mock_push_manifest.side_effect = [True, False]

    result = manifest.main()

    self.assertEqual(result, 1)
    self.assertEqual(mock_push_manifest.call_count, 2)

  @mock.patch('manifest.push_manifest')
  @mock.patch('subprocess.run')
  def test_main_all_push_failures(self, mock_run, mock_push_manifest):
    """Tests that main returns error code when all pushes fail."""
    mock_run.return_value.returncode = 0
    mock_push_manifest.return_value = False

    result = manifest.main()

    self.assertEqual(result, 1)
    self.assertEqual(mock_push_manifest.call_count, 2)

  @mock.patch('manifest.push_manifest')
  @mock.patch('subprocess.run')
  def test_main_processes_correct_images(self, mock_run, mock_push_manifest):
    """Tests that main processes the expected base images."""
    mock_run.return_value.returncode = 0
    mock_push_manifest.return_value = True

    manifest.main()

    # Verify the specific images are being processed
    called_images = [call[0][0] for call in mock_push_manifest.call_args_list]
    self.assertIn('gcr.io/oss-fuzz-base/base-builder', called_images)
    self.assertIn('gcr.io/oss-fuzz-base/base-runner', called_images)
    self.assertEqual(len(called_images), 2)


if __name__ == '__main__':
  unittest.main()
