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
"""Tests for base_runner_utils.py"""
import os
import unittest

import base_runner_utils
import config_utils
import test_helpers


class GetEnvTest(unittest.TestCase):
  """Tests for get_env."""

  def setUp(self):
    test_helpers.patch_environ(self)
    self.config = test_helpers.create_run_config(
        workspace='/workspace',
        sanitizer='address',
        language='c++',
        architecture='x86_64',
    )
    self.workspace = test_helpers.create_workspace('/workspace')

  def test_sanitizer_is_set(self):
    """Tests that SANITIZER is set correctly in the returned env."""
    env = base_runner_utils.get_env(self.config, self.workspace)
    self.assertEqual(env['SANITIZER'], self.config.sanitizer)

  def test_fuzzing_language_is_set(self):
    """Tests that FUZZING_LANGUAGE is set correctly in the returned env."""
    env = base_runner_utils.get_env(self.config, self.workspace)
    self.assertEqual(env['FUZZING_LANGUAGE'], self.config.language)

  def test_out_is_set(self):
    """Tests that OUT is set to the workspace.out path."""
    env = base_runner_utils.get_env(self.config, self.workspace)
    self.assertEqual(env['OUT'], self.workspace.out)

  def test_cifuzz_is_set_true(self):
    """Tests that CIFUZZ is set to 'True'."""
    env = base_runner_utils.get_env(self.config, self.workspace)
    self.assertEqual(env['CIFUZZ'], 'True')

  def test_fuzzing_engine_is_set(self):
    """Tests that FUZZING_ENGINE is set to the default engine."""
    env = base_runner_utils.get_env(self.config, self.workspace)
    self.assertEqual(env['FUZZING_ENGINE'], config_utils.DEFAULT_ENGINE)

  def test_architecture_is_set(self):
    """Tests that ARCHITECTURE is set correctly in the returned env."""
    env = base_runner_utils.get_env(self.config, self.workspace)
    self.assertEqual(env['ARCHITECTURE'], self.config.architecture)

  def test_fuzzer_args_is_set(self):
    """Tests that FUZZER_ARGS is set with rss_limit and timeout."""
    env = base_runner_utils.get_env(self.config, self.workspace)
    self.assertIn('FUZZER_ARGS', env)
    self.assertIn('-rss_limit_mb=2560', env['FUZZER_ARGS'])
    self.assertIn('-timeout=25', env['FUZZER_ARGS'])

  def test_env_contains_existing_variables(self):
    """Tests that the returned env inherits existing environment variables."""
    os.environ['MY_EXISTING_VAR'] = 'some_value'
    env = base_runner_utils.get_env(self.config, self.workspace)
    self.assertEqual(env['MY_EXISTING_VAR'], 'some_value')

  def test_different_sanitizer(self):
    """Tests that a different sanitizer is correctly reflected."""
    config = test_helpers.create_run_config(
        workspace='/workspace',
        sanitizer='memory',
        language='c++',
        architecture='x86_64',
    )
    env = base_runner_utils.get_env(config, self.workspace)
    self.assertEqual(env['SANITIZER'], 'memory')

  def test_different_language(self):
    """Tests that a different language is correctly reflected."""
    config = test_helpers.create_run_config(
        workspace='/workspace',
        sanitizer='address',
        language='python',
        architecture='x86_64',
    )
    env = base_runner_utils.get_env(config, self.workspace)
    self.assertEqual(env['FUZZING_LANGUAGE'], 'python')


if __name__ == '__main__':
  unittest.main()
