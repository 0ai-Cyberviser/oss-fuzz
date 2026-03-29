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
"""Tests for retry module."""

import unittest
from unittest import mock

import retry


class SleepTest(unittest.TestCase):
  """Tests for sleep function."""

  @mock.patch('time.sleep')
  def test_sleep_calls_time_sleep(self, mock_sleep):
    """Test that sleep() correctly wraps time.sleep()."""
    retry.sleep(5.5)
    mock_sleep.assert_called_once_with(5.5)

  @mock.patch('time.sleep')
  def test_sleep_with_zero(self, mock_sleep):
    """Test sleep with zero seconds."""
    retry.sleep(0)
    mock_sleep.assert_called_once_with(0)

  @mock.patch('time.sleep')
  def test_sleep_with_float(self, mock_sleep):
    """Test sleep with fractional seconds."""
    retry.sleep(0.001)
    mock_sleep.assert_called_once_with(0.001)


class GetDelayTest(unittest.TestCase):
  """Tests for get_delay function."""

  def test_get_delay_first_try(self):
    """Test delay calculation for first retry."""
    # First try should have no backoff applied
    self.assertEqual(retry.get_delay(1, delay=2, backoff=2), 2)

  def test_get_delay_second_try(self):
    """Test delay calculation for second retry."""
    # Second try: delay * backoff^(2-1) = 2 * 2^1 = 4
    self.assertEqual(retry.get_delay(2, delay=2, backoff=2), 4)

  def test_get_delay_third_try(self):
    """Test delay calculation for third retry."""
    # Third try: delay * backoff^(3-1) = 2 * 2^2 = 8
    self.assertEqual(retry.get_delay(3, delay=2, backoff=2), 8)

  def test_get_delay_exponential_backoff(self):
    """Test exponential backoff progression."""
    self.assertEqual(retry.get_delay(1, delay=1, backoff=3), 1)
    self.assertEqual(retry.get_delay(2, delay=1, backoff=3), 3)
    self.assertEqual(retry.get_delay(3, delay=1, backoff=3), 9)
    self.assertEqual(retry.get_delay(4, delay=1, backoff=3), 27)

  def test_get_delay_no_backoff(self):
    """Test with backoff=1 (constant delay)."""
    self.assertEqual(retry.get_delay(1, delay=5, backoff=1), 5)
    self.assertEqual(retry.get_delay(2, delay=5, backoff=1), 5)
    self.assertEqual(retry.get_delay(3, delay=5, backoff=1), 5)

  def test_get_delay_fractional_backoff(self):
    """Test with fractional backoff."""
    self.assertEqual(retry.get_delay(1, delay=10, backoff=1.5), 10)
    self.assertEqual(retry.get_delay(2, delay=10, backoff=1.5), 15)
    self.assertAlmostEqual(retry.get_delay(3, delay=10, backoff=1.5), 22.5)


class WrapDecoratorTest(unittest.TestCase):
  """Tests for wrap decorator."""

  def setUp(self):
    """Set up test fixtures."""
    self.call_count = 0
    self.exception_count = 0

  @mock.patch('retry.sleep')
  def test_successful_function_no_retry(self, mock_sleep):
    """Test function that succeeds on first try."""

    @retry.wrap(retries=3, delay=1)
    def successful_func():
      self.call_count += 1
      return 'success'

    result = successful_func()
    self.assertEqual(result, 'success')
    self.assertEqual(self.call_count, 1)
    mock_sleep.assert_not_called()

  @mock.patch('retry.sleep')
  def test_function_succeeds_after_retries(self, mock_sleep):
    """Test function that fails twice then succeeds."""

    @retry.wrap(retries=3, delay=1, backoff=2)
    def eventually_successful():
      self.call_count += 1
      if self.call_count < 3:
        raise ValueError('Temporary failure')
      return 'success'

    result = eventually_successful()
    self.assertEqual(result, 'success')
    self.assertEqual(self.call_count, 3)
    # Should sleep twice (after first and second failures)
    self.assertEqual(mock_sleep.call_count, 2)
    # Check backoff: first delay=1, second delay=2
    mock_sleep.assert_any_call(1)
    mock_sleep.assert_any_call(2)

  @mock.patch('retry.sleep')
  def test_function_fails_all_retries(self, mock_sleep):
    """Test function that fails all retry attempts."""

    @retry.wrap(retries=2, delay=1)
    def always_fails():
      self.call_count += 1
      raise RuntimeError('Permanent failure')

    with self.assertRaises(RuntimeError) as context:
      always_fails()

    self.assertEqual(str(context.exception), 'Permanent failure')
    self.assertEqual(self.call_count, 3)  # Initial + 2 retries
    self.assertEqual(mock_sleep.call_count, 2)

  @mock.patch('retry.sleep')
  def test_retry_on_false(self, mock_sleep):
    """Test retry_on_false parameter."""

    @retry.wrap(retries=2, delay=1, retry_on_false=True)
    def returns_false_then_true():
      self.call_count += 1
      if self.call_count < 2:
        return False
      return True

    result = returns_false_then_true()
    self.assertTrue(result)
    self.assertEqual(self.call_count, 2)
    mock_sleep.assert_called_once_with(1)

  @mock.patch('retry.sleep')
  def test_retry_on_false_exhausted(self, mock_sleep):
    """Test retry_on_false when all retries return False."""

    @retry.wrap(retries=2, delay=1, retry_on_false=True)
    def always_returns_false():
      self.call_count += 1
      return False

    result = always_returns_false()
    self.assertFalse(result)
    self.assertEqual(self.call_count, 3)
    self.assertEqual(mock_sleep.call_count, 2)

  @mock.patch('retry.sleep')
  def test_specific_exception_type(self, mock_sleep):
    """Test retry only on specific exception type."""

    @retry.wrap(retries=2, delay=1, exception_type=ValueError)
    def raises_wrong_exception():
      self.call_count += 1
      raise TypeError('Wrong exception type')

    # Should not retry on TypeError
    with self.assertRaises(TypeError):
      raises_wrong_exception()

    self.assertEqual(self.call_count, 1)
    mock_sleep.assert_not_called()

  @mock.patch('retry.sleep')
  def test_specific_exception_type_match(self, mock_sleep):
    """Test retry with matching exception type."""

    @retry.wrap(retries=2, delay=1, exception_type=ValueError)
    def raises_matching_exception():
      self.call_count += 1
      if self.call_count < 2:
        raise ValueError('Matching exception')
      return 'success'

    result = raises_matching_exception()
    self.assertEqual(result, 'success')
    self.assertEqual(self.call_count, 2)
    mock_sleep.assert_called_once()

  @mock.patch('retry.sleep')
  def test_zero_retries(self, mock_sleep):
    """Test with zero retries (only one attempt)."""

    @retry.wrap(retries=0, delay=1)
    def fails_immediately():
      self.call_count += 1
      raise ValueError('Immediate failure')

    with self.assertRaises(ValueError):
      fails_immediately()

    self.assertEqual(self.call_count, 1)
    mock_sleep.assert_not_called()

  def test_invalid_delay_assertion(self):
    """Test that invalid delay raises AssertionError."""
    with self.assertRaises(AssertionError):

      @retry.wrap(retries=1, delay=0)
      def dummy_func():
        pass

  def test_invalid_backoff_assertion(self):
    """Test that invalid backoff raises AssertionError."""
    with self.assertRaises(AssertionError):

      @retry.wrap(retries=1, delay=1, backoff=0.5)
      def dummy_func():
        pass

  def test_invalid_retries_assertion(self):
    """Test that negative retries raises AssertionError."""
    with self.assertRaises(AssertionError):

      @retry.wrap(retries=-1, delay=1)
      def dummy_func():
        pass

  @mock.patch('retry.sleep')
  def test_function_with_arguments(self, mock_sleep):
    """Test decorated function with arguments."""

    @retry.wrap(retries=2, delay=1)
    def func_with_args(a, b, keyword=None):
      self.call_count += 1
      if self.call_count < 2:
        raise ValueError('Retry needed')
      return a + b + (keyword or 0)

    result = func_with_args(1, 2, keyword=3)
    self.assertEqual(result, 6)
    self.assertEqual(self.call_count, 2)

  @mock.patch('retry.sleep')
  def test_function_preserves_docstring(self, mock_sleep):
    """Test that decorator preserves function metadata."""

    @retry.wrap(retries=1, delay=1)
    def documented_func():
      """This is a docstring."""
      return 'result'

    self.assertEqual(documented_func.__doc__, 'This is a docstring.')
    self.assertEqual(documented_func.__name__, 'documented_func')


class WrapGeneratorTest(unittest.TestCase):
  """Tests for wrap decorator with generator functions."""

  def setUp(self):
    """Set up test fixtures."""
    self.call_count = 0
    self.yield_count = 0

  @mock.patch('retry.sleep')
  def test_successful_generator_no_retry(self, mock_sleep):
    """Test generator that succeeds on first try."""

    @retry.wrap(retries=3, delay=1)
    def successful_generator():
      self.call_count += 1
      for i in range(3):
        yield i

    results = list(successful_generator())
    self.assertEqual(results, [0, 1, 2])
    self.assertEqual(self.call_count, 1)
    mock_sleep.assert_not_called()

  @mock.patch('retry.sleep')
  def test_generator_fails_then_succeeds(self, mock_sleep):
    """Test generator that fails after yielding some values."""

    @retry.wrap(retries=2, delay=1)
    def partially_successful_generator():
      self.call_count += 1
      for i in range(5):
        if i == 2 and self.call_count < 2:
          raise ValueError('Temporary failure at i=2')
        yield i

    results = list(partially_successful_generator())
    self.assertEqual(results, [0, 1, 2, 3, 4])
    # Should be called twice (initial + 1 retry)
    self.assertEqual(self.call_count, 2)
    mock_sleep.assert_called_once()

  @mock.patch('retry.sleep')
  def test_generator_exhausts_retries(self, mock_sleep):
    """Test generator that fails on all retry attempts."""

    @retry.wrap(retries=2, delay=1)
    def always_failing_generator():
      self.call_count += 1
      yield 1
      yield 2
      raise RuntimeError('Persistent failure')

    gen = always_failing_generator()
    results = []
    with self.assertRaises(RuntimeError):
      for value in gen:
        results.append(value)

    # Should collect values from first attempt only (not duplicated)
    self.assertEqual(results, [1, 2])
    self.assertEqual(self.call_count, 3)  # Initial + 2 retries
    self.assertEqual(mock_sleep.call_count, 2)

  @mock.patch('retry.sleep')
  def test_generator_with_retry_on_false_assertion(self, mock_sleep):
    """Test that retry_on_false is not allowed with generators."""

    with self.assertRaises(AssertionError):

      @retry.wrap(retries=1, delay=1, retry_on_false=True)
      def invalid_generator():
        yield 1

      # Trigger the generator to hit the assertion
      list(invalid_generator())

  @mock.patch('retry.sleep')
  def test_generator_resumes_from_failure_point(self, mock_sleep):
    """Test that generator resumes and doesn't re-yield values."""

    @retry.wrap(retries=3, delay=1)
    def resume_generator():
      self.call_count += 1
      for i in range(5):
        # Fail on third element of first attempt
        if i == 3 and self.call_count == 1:
          raise ValueError('Fail at i=3 on first attempt')
        yield i

    results = list(resume_generator())
    # Should get all values without duplicates
    self.assertEqual(results, [0, 1, 2, 3, 4])
    self.assertEqual(self.call_count, 2)


class BackoffIntegrationTest(unittest.TestCase):
  """Integration tests for backoff behavior."""

  @mock.patch('retry.sleep')
  def test_complex_backoff_scenario(self, mock_sleep):
    """Test complex scenario with multiple retries and exponential backoff."""
    call_count = 0

    @retry.wrap(retries=4, delay=0.5, backoff=2)
    def complex_function():
      nonlocal call_count
      call_count += 1
      if call_count < 4:
        raise ConnectionError(f'Attempt {call_count} failed')
      return 'finally succeeded'

    result = complex_function()
    self.assertEqual(result, 'finally succeeded')
    self.assertEqual(call_count, 4)

    # Verify backoff delays: 0.5, 1.0, 2.0
    expected_delays = [0.5, 1.0, 2.0]
    actual_delays = [call[0][0] for call in mock_sleep.call_args_list]
    self.assertEqual(actual_delays, expected_delays)


if __name__ == '__main__':
  unittest.main()
