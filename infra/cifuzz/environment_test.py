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
"""Tests for environment.py"""
import os
import unittest

import environment
import test_helpers


class EvalValueTest(unittest.TestCase):
  """Tests for _eval_value."""

  def test_integer_string(self):
    """Tests that integer strings are evaluated to integers."""
    self.assertEqual(environment._eval_value('42'), 42)

  def test_float_string(self):
    """Tests that float strings are evaluated to floats."""
    self.assertAlmostEqual(environment._eval_value('3.14'), 3.14)

  def test_bool_true(self):
    """Tests that 'True' is evaluated to boolean True."""
    self.assertIs(environment._eval_value('True'), True)

  def test_bool_false(self):
    """Tests that 'False' is evaluated to boolean False."""
    self.assertIs(environment._eval_value('False'), False)

  def test_list_string(self):
    """Tests that a list string is evaluated to a list."""
    self.assertEqual(environment._eval_value('[1, 2, 3]'), [1, 2, 3])

  def test_plain_string(self):
    """Tests that a plain string that cannot be evaluated returns the string."""
    value = 'some-string-value'
    self.assertEqual(environment._eval_value(value), value)

  def test_empty_string(self):
    """Tests that an empty string returns an empty string."""
    self.assertEqual(environment._eval_value(''), '')

  def test_none_literal(self):
    """Tests that 'None' string is evaluated to Python None."""
    self.assertIsNone(environment._eval_value('None'))


class GetTest(unittest.TestCase):
  """Tests for get."""

  def setUp(self):
    test_helpers.patch_environ(self, empty=True)

  def test_unset_variable_returns_default(self):
    """Tests that an unset variable returns the default value."""
    self.assertIsNone(environment.get('UNSET_VAR_XYZ'))

  def test_unset_variable_returns_custom_default(self):
    """Tests that an unset variable returns the provided default."""
    self.assertEqual(environment.get('UNSET_VAR_XYZ', 'default'), 'default')

  def test_set_string_variable(self):
    """Tests that a set string variable returns the correct value."""
    os.environ['MY_TEST_VAR'] = 'hello'
    self.assertEqual(environment.get('MY_TEST_VAR'), 'hello')

  def test_set_integer_variable(self):
    """Tests that an integer string variable returns an integer."""
    os.environ['MY_INT_VAR'] = '100'
    self.assertEqual(environment.get('MY_INT_VAR'), 100)

  def test_set_bool_variable_true(self):
    """Tests that 'True' is returned as boolean True."""
    os.environ['MY_BOOL_VAR'] = 'True'
    self.assertIs(environment.get('MY_BOOL_VAR'), True)

  def test_set_bool_variable_false(self):
    """Tests that 'False' is returned as boolean False."""
    os.environ['MY_BOOL_VAR'] = 'False'
    self.assertIs(environment.get('MY_BOOL_VAR'), False)

  def test_default_not_used_when_var_set(self):
    """Tests that the default value is not used when the variable is set."""
    os.environ['MY_TEST_VAR'] = 'actual'
    self.assertEqual(environment.get('MY_TEST_VAR', 'default'), 'actual')


class GetBoolTest(unittest.TestCase):
  """Tests for get_bool."""

  def setUp(self):
    test_helpers.patch_environ(self)

  def test_unset_variable_returns_none_default(self):
    """Tests that an unset variable returns None by default."""
    self.assertIsNone(environment.get_bool('UNSET_VAR_XYZ'))

  def test_unset_variable_returns_custom_default(self):
    """Tests that an unset variable returns the provided default."""
    self.assertFalse(environment.get_bool('UNSET_VAR_XYZ', False))

  def test_true_literal(self):
    """Tests that boolean True value returns True."""
    os.environ['MY_BOOL_VAR'] = 'True'
    self.assertTrue(environment.get_bool('MY_BOOL_VAR'))

  def test_false_literal(self):
    """Tests that boolean False value returns False."""
    os.environ['MY_BOOL_VAR'] = 'False'
    self.assertFalse(environment.get_bool('MY_BOOL_VAR'))

  def test_true_lowercase(self):
    """Tests that 'true' (lowercase) returns True."""
    os.environ['MY_BOOL_VAR'] = 'true'
    self.assertTrue(environment.get_bool('MY_BOOL_VAR'))

  def test_false_lowercase(self):
    """Tests that 'false' (lowercase) returns False."""
    os.environ['MY_BOOL_VAR'] = 'false'
    self.assertFalse(environment.get_bool('MY_BOOL_VAR'))

  def test_invalid_value_raises_exception(self):
    """Tests that an invalid boolean string raises an Exception."""
    os.environ['MY_BOOL_VAR'] = 'invalid'
    with self.assertRaises(Exception):
      environment.get_bool('MY_BOOL_VAR')

  def test_integer_zero_is_false(self):
    """Tests that integer 0 (set as string '0') evaluates as False."""
    os.environ['MY_BOOL_VAR'] = '0'
    self.assertFalse(environment.get_bool('MY_BOOL_VAR'))

  def test_integer_one_is_true(self):
    """Tests that integer 1 (set as string '1') evaluates as True."""
    os.environ['MY_BOOL_VAR'] = '1'
    self.assertTrue(environment.get_bool('MY_BOOL_VAR'))

  def test_bool_true_default(self):
    """Tests that a True default is returned as True."""
    self.assertTrue(environment.get_bool('UNSET_VAR_XYZ', True))


if __name__ == '__main__':
  unittest.main()
