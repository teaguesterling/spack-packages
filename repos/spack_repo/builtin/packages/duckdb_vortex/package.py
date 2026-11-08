# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os

from spack_repo.builtin.packages.duckdb_extensions.package import (
    DuckdbExtensionPackage,
    published_binaries,
)

from spack.package import *


class DuckdbVortex(DuckdbExtensionPackage):
    """Adds support for reading and writing files using the Vortex file format."""

    homepage = "https://github.com/vortex-data/duckdb-vortex"

    license("MIT")

    with when("~prebuilt"):
        # The rust-version of vortex-duckdb. Its build.rs runs bindgen, which needs libclang.
        depends_on("rust@1.95:", type="build")
        depends_on("llvm+clang", type="build")

    published_binaries(
        "vortex",
        "2.0.0",
        {
            "linux_amd64": "9d5d6c429268188fc2e735947c383bbfa1a9abf09241437a83f0a5bbe089ad95",
            "linux_arm64": "eb1eb304ec9b15a73beccfbc1cb92ea2a9f3b9fdbf5677a7a05c6bf498274b6a",
            "osx_arm64": "03ae00b862c60245c304d094c81151f4fb51d8f822d07becad8373bc6238b419",
        },
    )

    duckdb_patches = True

    resource(
        name="extension_source",
        git="https://github.com/vortex-data/duckdb-vortex.git",
        commit="f56da1b2736ff2032db5c09a540303408c93f195",
        submodules=lambda package: ["vcpkg"],
        placement="extension_source",
        when="@2.0.0 ~prebuilt",
    )

    # CMakeLists.txt gets Corrosion with FetchContent, which a download cannot do here
    resource(
        name="corrosion",
        git="https://github.com/corrosion-rs/corrosion.git",
        tag="v0.5.2",
        commit="a1a1aaa057a5da656c06c3d8505b767a4e941709",
        placement="corrosion_source",
        when="@2.0.0 ~prebuilt",
    )

    # The 0.89.0 commit changed the vortex-duckdb revision in vortex-extension/Cargo.toml, but
    # not Cargo.lock. This patch is the minimal update of Cargo.lock that cargo makes for it.
    patch(
        "vortex-extension-0.89.0-cargo-lock.patch",
        working_dir="extension_source",
        when="@2.0.0 ~prebuilt",
    )

    def source_cmake_args(self):
        corrosion = join_path(self.stage.source_path, "corrosion_source")
        return [
            f"-DFETCHCONTENT_SOURCE_DIR_CORROSION={corrosion}",
            # Otherwise CMakeLists.txt runs git ls-remote to find the tag of the vortex-duckdb
            # revision in vortex-extension/Cargo.toml. 0.89.0 is the tag of that revision.
            "-DVORTEX_VERSION=0.89.0",
        ]

    def setup_build_environment(self, env: EnvironmentModifications) -> None:
        super().setup_build_environment(env)
        if self.spec.satisfies("~prebuilt"):
            env.set("CARGO_BUILD_JOBS", str(make_jobs))
            env.set("LIBCLANG_PATH", self._libclang_dir())

    def _libclang_dir(self):
        # bindgen loads libclang.so, libclang.so.* or libclang-*.so*. An external llvm can keep
        # it below its prefix: with prefix /usr, Ubuntu has it in /usr/lib/llvm-18/lib.
        prefix = self.spec["llvm"].prefix
        patterns = ["libclang.so", "libclang.so.*", "libclang-[0-9]*.so*"]
        for root, recursive in ((prefix.lib, False), (prefix.lib64, False), (prefix, True)):
            if os.path.isdir(root):
                found = find(root, patterns, recursive=recursive)
                if found:
                    return os.path.dirname(found[0])
        raise InstallError(f"libclang not found under {prefix}")

    @when("~prebuilt")
    def patch(self):
        cmake_lists = join_path("extension_source", "CMakeLists.txt")
        with open(cmake_lists) as source:
            text = source.read()
        # Use the crate versions in Cargo.lock
        old = "    CRATE_TYPES ${VORTEX_LIB_TYPE}\n"
        if text.count(old) != 1:
            raise InstallError(f"{cmake_lists} does not have exactly one copy of: {old}")
        text = text.replace(old, old + "    LOCKED\n")
        with open(cmake_lists, "w") as output:
            output.write(text)
