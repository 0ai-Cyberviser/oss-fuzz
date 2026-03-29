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
"""Tests for platform_config.gcb."""
import os
import sys
import unittest

# pylint: disable=wrong-import-position
INFRA_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(INFRA_DIR)

import platform_config.gcb
import test_helpers


class GcbPlatformConfigTest(unittest.TestCase):
  """Tests for Google Cloud Build PlatformConfig."""

  def setUp(self):
    test_helpers.patch_environ(self, empty=True)
    self.platform_conf = platform_config.gcb.PlatformConfig()

  def test_project_src_path_default(self):
    """Tests that project_src_path defaults to '/workspace'."""
    self.assertEqual(self.platform_conf.project_src_path, '/workspace')

  def test_project_src_path_custom(self):
    """Tests that project_src_path uses PROJECT_SRC_PATH if set."""
    os.environ['PROJECT_SRC_PATH'] = '/custom/path'
    self.assertEqual(self.platform_conf.project_src_path, '/custom/path')

  def test_workspace_default(self):
    """Tests that workspace defaults to '/builder/home'."""
    self.assertEqual(self.platform_conf.workspace, '/builder/home')

  def test_workspace_custom(self):
    """Tests that workspace uses WORKSPACE env var if set."""
    os.environ['WORKSPACE'] = '/my/workspace'
    self.assertEqual(self.platform_conf.workspace, '/my/workspace')

  def test_filestore_default(self):
    """Tests that filestore defaults to 'gsutil'."""
    self.assertEqual(self.platform_conf.filestore, 'gsutil')

  def test_filestore_custom(self):
    """Tests that filestore uses FILESTORE env var if set."""
    os.environ['FILESTORE'] = 'custom-filestore'
    self.assertEqual(self.platform_conf.filestore, 'custom-filestore')


if __name__ == '__main__':
  unittest.main()
