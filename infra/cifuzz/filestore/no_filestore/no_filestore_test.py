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
"""Tests for filestore/no_filestore."""
import os
import sys
import tempfile
import unittest

# pylint: disable=wrong-import-position
INFRA_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))))
sys.path.append(INFRA_DIR)

from filestore import no_filestore
import test_helpers


class NoFilestoreTest(unittest.TestCase):
  """Tests for NoFilestore."""

  def setUp(self):
    config = test_helpers.create_run_config(workspace='/workspace')
    self.filestore = no_filestore.NoFilestore(config)

  def test_upload_crashes_is_noop(self):
    """Tests that upload_crashes returns None (noop) without error."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      result = self.filestore.upload_crashes('name', tmp_dir)
      self.assertIsNone(result)

  def test_upload_corpus_is_noop(self):
    """Tests that upload_corpus returns None (noop) without error."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      result = self.filestore.upload_corpus('name', tmp_dir)
      self.assertIsNone(result)

  def test_upload_build_is_noop(self):
    """Tests that upload_build returns None (noop) without error."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      result = self.filestore.upload_build('name', tmp_dir)
      self.assertIsNone(result)

  def test_upload_coverage_is_noop(self):
    """Tests that upload_coverage returns None (noop) without error."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      result = self.filestore.upload_coverage('name', tmp_dir)
      self.assertIsNone(result)

  def test_download_corpus_is_noop(self):
    """Tests that download_corpus returns None (noop) without error."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      result = self.filestore.download_corpus('name', tmp_dir)
      self.assertIsNone(result)

  def test_download_build_is_noop(self):
    """Tests that download_build returns None (noop) without error."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      result = self.filestore.download_build('name', tmp_dir)
      self.assertIsNone(result)

  def test_download_coverage_is_noop(self):
    """Tests that download_coverage returns None (noop) without error."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      result = self.filestore.download_coverage('name', tmp_dir)
      self.assertIsNone(result)

  def test_upload_corpus_with_replace_is_noop(self):
    """Tests that upload_corpus with replace=True also returns None."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      result = self.filestore.upload_corpus('name', tmp_dir, replace=True)
      self.assertIsNone(result)


if __name__ == '__main__':
  unittest.main()
