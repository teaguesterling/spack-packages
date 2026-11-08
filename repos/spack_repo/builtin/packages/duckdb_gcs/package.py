# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.packages.duckdb_extensions.package import (
    DuckdbCommunityExtensionPackage,
    published_binaries,
)

from spack.package import *


class DuckdbGcs(DuckdbCommunityExtensionPackage):
    """Adds support for Google Cloud Storage."""

    homepage = "https://github.com/northpolesec/duckdb-gcs"

    license("MIT")

    # The CMake config of the SDK names libcurl.a, which needs these
    source_link_libraries = [("openssl", "ssl"), ("openssl", "crypto"), ("zlib-api", "z")]

    with when("~prebuilt"):
        depends_on("curl~nghttp2", type="build")
        depends_on("nlohmann-json", type="build")
        depends_on("zlib-api", type="build")
    with when("link_dependencies=static"):
        # The versions in the vcpkg baseline of vcpkg.json. storage_grpc adds storage, and
        # CMakeLists.txt needs both on Linux. A static library of the stack that the others
        # need must be static too, or the extension links its shared library.
        depends_on(
            "google-cloud-cpp@2.37.0~shared+pic cxxstd=17 libraries=storage_grpc", type="build"
        )
        depends_on("grpc@1.76.0~shared~systemd~download_archives cxxstd=17", type="build")
        depends_on("protobuf@33~shared", type="build")
        depends_on("abseil-cpp@20260107.1~shared+pic", type="build")
        depends_on("re2~shared+pic", type="build")
        depends_on("c-ares~shared+pic", type="build")
        depends_on("google-crc32c~shared+pic", type="build")
    with when("link_dependencies=shared"):
        depends_on("google-cloud-cpp@2.37.0+shared cxxstd=17 libraries=storage_grpc", type="link")
        depends_on("grpc@1.76.0+shared~systemd~download_archives cxxstd=17", type="link")
        depends_on("protobuf@33+shared", type="link")
        depends_on("abseil-cpp@20260107.1+shared", type="link")
        depends_on("curl", type="link")
        depends_on("zlib-api", type="link")

    published_binaries(
        "gcs",
        "2.0.0",
        {
            "linux_amd64": "9c8d26732031ce4f9229b45d40a7c23e95021992a1397318c335617d0f211117",
            "linux_arm64": "c959b182a85112b98c7e49b2fb91af46a8f6ed83f21b0930b53f8cad7db7450f",
            "osx_amd64": "9b5ce254b3ea085701b4b346125383d040025ead6eb85eb7205a3cbf6f0a0e08",
            "osx_arm64": "1a01ebb6aae74973e67873bb674a58dbed1e7ded84e454905a9a8864a8917a99",
        },
        repository="community",
    )

    resource(
        name="extension_source",
        git="https://github.com/northpolesec/duckdb-gcs.git",
        commit="f55eef6635f5b613d7cb90a98fe2ed7afcd0f0c8",
        placement="extension_source",
        when="@2.0.0 ~prebuilt",
    )

    @when("~prebuilt")
    def patch(self):
        # The extension installs this target in the DuckDB export set. Its interface include
        # directory is a target name, which CMake makes a path in the source tree, and CMake
        # refuses that path in an export. Upstream CI builds the extension outside the DuckDB
        # source tree, so the path is outside it there. The include directories come from
        # target_link_libraries, so this line adds only a directory that does not exist.
        filter_file(
            "target_include_directories(${EXTENSION_NAME} PUBLIC google-cloud-cpp::storage)",
            "",
            "extension_source/CMakeLists.txt",
            string=True,
        )
