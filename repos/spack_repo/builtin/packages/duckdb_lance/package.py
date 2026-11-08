# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.packages.duckdb_extensions.package import (
    DuckdbExtensionPackage,
    published_binaries,
)

from spack.package import *


class DuckdbLance(DuckdbExtensionPackage):
    """Adds support for querying Lance datasets."""

    homepage = "https://github.com/lance-format/lance-duckdb"

    license("Apache-2.0")

    with when("~prebuilt"):
        # The rust-version of the lance crate in Cargo.lock
        depends_on("rust@1.91:", type="build")
        # prost-build runs protoc. The crates build their own copies of aws-lc, ring, zstd, lz4,
        # bzip2 and liblzma, as the published binary does.
        depends_on("protobuf", type="build")

    published_binaries(
        "lance",
        "2.0.0",
        {
            "linux_amd64": "fa013aee19031a8f8c250f787689aa03993e1ced5dbf4a57bfc44f4ce4e52a3a",
            "linux_arm64": "a48b6a1fd4c9da63149530707850a99c9706583b3ec0afbcf87a6c8961bb5aff",
            "osx_arm64": "c025118569d040af85915eb5f7903c9069b8df2e95ae1b1028ff06a31bbd27d1",
        },
    )

    resource(
        name="extension_source",
        git="https://github.com/lance-format/lance-duckdb.git",
        commit="86118537da79138e6ec5c7358f2384c7ae650ab0",
        placement="extension_source",
        when="@2.0.0 ~prebuilt",
    )

    def setup_build_environment(self, env: EnvironmentModifications) -> None:
        super().setup_build_environment(env)
        if self.spec.satisfies("~prebuilt"):
            env.set("CARGO_BUILD_JOBS", str(make_jobs))
            # CMakeLists.txt passes this to cargo
            env.set("PROTOC", self.spec["protobuf"].prefix.bin.protoc)
            # Without this, liblzma-sys links a shared liblzma that pkg-config finds
            env.set("LZMA_API_STATIC", "1")

    @when("~prebuilt")
    def patch(self):
        # Use the crate versions in Cargo.lock
        filter_file(r"cargo build$", "cargo build --locked", "extension_source/CMakeLists.txt")
