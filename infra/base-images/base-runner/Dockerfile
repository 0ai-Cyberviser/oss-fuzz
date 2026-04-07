# Copyright 2016 Google Inc.
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
#
################################################################################

# Build rust stuff in its own image. We only need the resulting binaries.
# Keeping the rust toolchain in the image wastes 1 GB.
FROM gcr.io/oss-fuzz-base/base-image as temp-runner-binary-builder

RUN apt-get update && apt-get install -y cargo libyaml-dev
RUN cargo install rustfilt

# Using multi-stage build to copy some LLVM binaries needed in the runner image.
FROM gcr.io/oss-fuzz-base/base-clang AS base-clang
FROM gcr.io/oss-fuzz-base/base-builder-ruby AS base-ruby

# The base builder image compiles a specific Python version. Using a multi-stage build
# to copy that same Python interpreter into the runner image saves build time and keeps
# the Python versions in sync.
FROM gcr.io/oss-fuzz-base/base-builder AS base-builder

# Real image that will be used later.
FROM gcr.io/oss-fuzz-base/base-image

COPY --from=temp-runner-binary-builder /root/.cargo/bin/rustfilt /usr/local/bin

# Copy the binaries needed for code coverage and crash symbolization.
COPY --from=base-clang /usr/local/bin/llvm-cov \
     /usr/local/bin/llvm-profdata \
     /usr/local/bin/llvm-symbolizer \
     /usr/local/bin/

# Copy the pre-compiled Python binaries and libraries
COPY --from=base-builder /usr/local/bin/python3.11 /usr/local/bin/python3.11
COPY --from=base-builder /usr/local/lib/libpython3.11.so.1.0 /usr/local/lib/libpython3.11.so.1.0
COPY --from=base-builder /usr/local/include/python3.11 /usr/local/include/python3.11
COPY --from=base-builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=base-builder /usr/local/bin/pip3 /usr/local/bin/pip3

# Create symbolic links to ensure compatibility
RUN ldconfig && \
    ln -s /usr/local/bin/python3.11 /usr/local/bin/python3 && \
    ln -s /usr/local/bin/python3.11 /usr/local/bin/python

COPY install_deps.sh /
RUN /install_deps.sh && rm /install_deps.sh

ENV CODE_COVERAGE_SRC=/opt/code_coverage
ARG CODE_COVERAGE_REV=edba4873b5e8a390e977a64c522db2df18a8b27d
# Pin coverage to the same as in the base builder:
# https://github.com/google/oss-fuzz/blob/master/infra/base-images/base-builder/install_python.sh#L22
# Retry clone and fetch up to 5 times each to handle transient HTTP errors
# (429 rate-limit, 403 access denied) from chromium.googlesource.com.
# If all attempts fail, skip code_coverage setup so non-coverage builds can proceed.
RUN set -eux; \
    clone_ok=false; \
    for i in 1 2 3 4 5; do \
      rm -rf "$CODE_COVERAGE_SRC"; \
      if git clone --filter=blob:none --no-checkout \
           https://chromium.googlesource.com/chromium/src/tools/code_coverage \
           "$CODE_COVERAGE_SRC"; then \
        clone_ok=true; \
        break; \
      fi; \
      echo "Clone attempt $i failed"; \
      if [ "$i" -lt 5 ]; then echo "retrying in $((i * 15))s..."; sleep $((i * 15)); fi; \
    done; \
    if [ "$clone_ok" = "true" ]; then \
      cd "$CODE_COVERAGE_SRC"; \
      fetch_ok=false; \
      for i in 1 2 3 4 5; do \
        if git fetch --depth=1 origin "$CODE_COVERAGE_REV"; then \
          fetch_ok=true; \
          break; \
        fi; \
        echo "Fetch attempt $i failed"; \
        if [ "$i" -lt 5 ]; then echo "retrying in $((i * 15))s..."; sleep $((i * 15)); fi; \
      done; \
      if [ "$fetch_ok" = "true" ]; then \
        git checkout "$CODE_COVERAGE_REV" && \
        pip3 install wheel && \
        sed -i 's/Jinja2==2.10/Jinja2==2.10.3/' requirements.txt && \
        pip3 install -r requirements.txt && \
        pip3 install MarkupSafe==2.0.1 && \
        pip3 install coverage==6.3.2; \
      else \
        echo "WARNING: All fetch attempts failed. Skipping code_coverage setup."; \
        rm -rf "$CODE_COVERAGE_SRC"; \
      fi; \
    else \
      echo "WARNING: All clone attempts failed. Skipping code_coverage setup."; \
    fi

# Default environment options for various sanitizers.
# Note that these match the settings used in ClusterFuzz and
# shouldn't be changed unless a corresponding change is made on
# ClusterFuzz side as well.
ENV ASAN_OPTIONS="alloc_dealloc_mismatch=0:allocator_may_return_null=1:allocator_release_to_os_interval_ms=500:check_malloc_usable_size=0:detect_container_overflow=1:detect_odr_violation=0:detect_leaks=1:detect_stack_use_after_return=1:fast_unwind_on_fatal=0:handle_abort=1:handle_segv=1:handle_sigill=1:max_uar_stack_size_log=16:print_scariness=1:quarantine_size_mb=10:strict_memcmp=1:strip_path_prefix=/workspace/:symbolize=1:use_sigaltstack=1:dedup_token_length=3"
ENV MSAN_OPTIONS="print_stats=1:strip_path_prefix=/workspace/:symbolize=1:dedup_token_length=3"
ENV UBSAN_OPTIONS="print_stacktrace=1:print_summary=1:silence_unsigned_overflow=1:strip_path_prefix=/workspace/:symbolize=1:dedup_token_length=3"
ENV FUZZER_ARGS="-rss_limit_mb=2560 -timeout=25"
ENV AFL_FUZZER_ARGS="-m none"

# Set up Golang environment variables (copied from /root/.bash_profile).
ENV GOPATH /root/go

# /root/.go/bin is for the standard Go binaries (i.e. go, gofmt, etc).
# $GOPATH/bin is for the binaries from the dependencies installed via "go get".
ENV PATH $PATH:$GOPATH/bin
COPY gocoverage $GOPATH/gocoverage

COPY install_go.sh /
RUN /install_go.sh && rm -rf /install_go.sh /root/.go

# Install OpenJDK 15 and trim its size by removing unused components.
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV JAVA_15_HOME=/usr/lib/jvm/java-15-openjdk-amd64
ENV JVM_LD_LIBRARY_PATH=$JAVA_HOME/lib/server
ENV PATH=$PATH:$JAVA_HOME/bin

COPY install_java.sh /
RUN /install_java.sh && rm /install_java.sh

# Install JaCoCo for JVM coverage.
RUN wget https://repo1.maven.org/maven2/org/jacoco/org.jacoco.cli/0.8.7/org.jacoco.cli-0.8.7-nodeps.jar -O /opt/jacoco-cli.jar && \
    wget https://repo1.maven.org/maven2/org/jacoco/org.jacoco.agent/0.8.7/org.jacoco.agent-0.8.7-runtime.jar -O /opt/jacoco-agent.jar && \
    echo "37df187b76888101ecd745282e9cd1ad4ea508d6  /opt/jacoco-agent.jar" | shasum --check && \
    echo "c1814e7bba5fd8786224b09b43c84fd6156db690  /opt/jacoco-cli.jar" | shasum --check

COPY install_javascript.sh /
RUN /install_javascript.sh && rm /install_javascript.sh

# Copy built ruby. It is up to the fuzzing harnesses
# themselves to set GEM_HOME and GEM_PATH appropriately, as this depends
# on how the harnesses are packaged.
COPY --from=base-ruby /usr/local/bin/ruby /usr/local/bin/ruby
COPY --from=base-ruby /usr/local/bin/gem /usr/local/bin/gem
COPY --from=base-ruby /usr/local/lib/ruby /usr/local/lib/ruby
COPY --from=base-ruby /usr/local/include/ruby-3.3.0 /usr/local/include/ruby-3.3.0

RUN apt-get update && apt-get install -y luarocks

# Do this last to make developing these files easier/faster due to caching.
COPY bad_build_check \
    coverage \
    coverage_helper \
    download_corpus \
    jacoco_report_converter.py \
    nyc_report_converter.py \
    rcfilt \
    reproduce \
    run_fuzzer \
    parse_options.py \
    generate_differential_cov_report.py \
    profraw_update.py \
    targets_list \
    test_all.py \
    test_one.py \
    python_coverage_runner_help.py \
    /usr/local/bin/
