#!/usr/bin/python3
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
"""Advanced configurable Atheris coverage fuzzer for ClusterFuzzLite."""

import atheris
import json
import logging
import os
import sys
from unittest import mock

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Configurable via environment variables (set in Dockerfile or GitHub Actions).
REPO_PATH = os.getenv('REPO_PATH', '/src')
PROJECT_NAME = os.getenv('PROJECT_NAME', 'default-project')
TARGET_NAME = os.getenv('TARGET_NAME', 'fuzz-target')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cifuzz'))

with atheris.instrument_imports():
  import get_coverage

# Mock the stats URL to avoid network dependency (fixes google#11649).
with mock.patch('get_coverage._get_oss_fuzz_fuzzer_stats_dir_url',
                return_value=os.getenv('OSS_FUZZ_STATS_URL', 'randomurl')):
  oss_fuzz_coverage = get_coverage.OSSFuzzCoverage(REPO_PATH, PROJECT_NAME)


def TestOneInput(data):
  """Fuzz target that exercises coverage JSON parsing."""
  try:
    decoded_json = json.loads(data)
  except (json.decoder.JSONDecodeError, UnicodeDecodeError):
    return oss_fuzz_coverage.get_files_covered_by_target(TARGET_NAME)

  with mock.patch('get_coverage.OSSFuzzCoverage.get_target_coverage',
                  return_value=decoded_json):
    covered_files = oss_fuzz_coverage.get_files_covered_by_target(TARGET_NAME)
    logging.info('Coverage collected: %d files for %s', len(covered_files),
                 TARGET_NAME)
    return covered_files


def main():
  atheris.Setup(sys.argv, TestOneInput, enable_python_coverage=True)
  logging.info('Starting advanced Atheris coverage fuzzer for %s/%s',
               PROJECT_NAME, TARGET_NAME)
  atheris.Fuzz()


if __name__ == '__main__':
  main()
