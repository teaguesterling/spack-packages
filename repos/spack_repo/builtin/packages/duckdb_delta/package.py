# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.packages.duckdb_extensions.package import (
    DuckdbExtensionPackage,
    published_binaries,
)

from spack.package import *


class DuckdbDelta(DuckdbExtensionPackage):
    """Adds support for Delta Lake."""

    homepage = "https://github.com/duckdb/duckdb-delta"

    license("MIT")

    with when("~prebuilt"):
        # The rust-version of the delta-kernel-rs workspace. The crates build their own copies of
        # aws-lc, ring and zstd, as the published binary does, so they need no other library.
        depends_on("rust@1.88:", type="build")

    published_binaries(
        "delta",
        "2.0.0",
        {
            "linux_amd64": "418d8f21fe10a6f49d200d76b745fc7f1ca916daa5d404b18c46e0f51cffcc7d",
            "linux_arm64": "7dc29ad733d7967984096f4dfd715c3f3404d43ac11b53350ad73fa42b8b90d3",
            "osx_amd64": "2860ad9152ec9aae39cec2f57c14a70af9f40a6530db25d82e7d279b336d6434",
            "osx_arm64": "4396f8cb5fe223214adf5c3be5edbfccf5d599ca877ccdcbb6a2c5adb5552423",
        },
    )

    resource(
        name="extension_source",
        git="https://github.com/duckdb/duckdb-delta.git",
        commit="9dcfb65b99fcafaa068222c2490abc143da4cc8e",
        placement="extension_source",
        when="@2.0.0 ~prebuilt",
    )
    # The tag v0.28.0, which CMakeLists.txt clones with ExternalProject
    resource(
        name="delta_kernel",
        git="https://github.com/delta-io/delta-kernel-rs.git",
        commit="b77d6518b2ae76bcb8796256666ad0de3f7f654b",
        placement="delta_kernel_source",
        when="@2.0.0 ~prebuilt",
    )

    def setup_build_environment(self, env: EnvironmentModifications) -> None:
        super().setup_build_environment(env)
        if self.spec.satisfies("~prebuilt"):
            env.set("CARGO_BUILD_JOBS", str(make_jobs))

    @when("~prebuilt")
    def patch(self):
        cmake_lists = join_path("extension_source", "CMakeLists.txt")
        with open(cmake_lists) as source:
            text = source.read()
        kernel = join_path(self.stage.source_path, "delta_kernel_source")
        replacements = [
            # ExternalProject copies the resource, so the paths in the build tree stay the same
            (
                'GIT_REPOSITORY "https://github.com/delta-io/delta-kernel-rs"\n'
                "  GIT_TAG v0.28.0\n",
                f"DOWNLOAD_COMMAND ${{CMAKE_COMMAND}} -E copy_directory {kernel} <SOURCE_DIR>\n",
            ),
            # Use the crate versions in Cargo.lock
            (
                "cargo build\n    --package delta_kernel_ffi",
                "cargo build --locked\n    --package delta_kernel_ffi",
            ),
            # This builds the acceptance tests, and their build script downloads test data. The
            # extension does not use them.
            (
                "  # Build DATs\n  COMMAND\n"
                "    ${CMAKE_COMMAND} -E env ${RUST_UNSET_ENV_VARS} ${RUST_ENV_VARS} cargo build\n"
                "    --manifest-path="
                "${CMAKE_BINARY_DIR}/rust/src/delta_kernel/acceptance/Cargo.toml\n",
                "",
            ),
        ]
        for old, new in replacements:
            if text.count(old) != 1:
                raise InstallError(f"{cmake_lists} does not have exactly one copy of: {old}")
            text = text.replace(old, new)
        with open(cmake_lists, "w") as output:
            output.write(text)
