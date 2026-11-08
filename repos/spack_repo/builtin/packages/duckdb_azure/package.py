# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.packages.duckdb_extensions.package import (
    DuckdbExtensionPackage,
    published_binaries,
)

from spack.package import *


class DuckdbAzure(DuckdbExtensionPackage):
    """Adds a filesystem abstraction for Azure blob storage to DuckDB."""

    homepage = "https://github.com/duckdb/duckdb-azure"

    license("MIT")

    # The SDK configs find libcurl.a and libxml2.a, which need these
    source_link_libraries = [
        ("libiconv", "iconv"),
        ("openssl", "ssl"),
        ("openssl", "crypto"),
        ("zlib-api", "z"),
    ]

    with when("~prebuilt"):
        depends_on("curl~nghttp2", type="build")
        depends_on("libiconv", type="build")
        depends_on("zlib-api", type="build")
    with when("link_dependencies=static"):
        # The versions in the vcpkg baseline of vcpkg.json. A static library of the SDK that
        # the others need must be static too, or the extension links its shared library.
        depends_on("azure-core-cpp@1.16.3~shared+pic", type="build")
        depends_on("azure-identity-cpp@1.13.3~shared+pic", type="build")
        depends_on("azure-storage-common-cpp@12.14.0~shared+pic", type="build")
        depends_on("azure-storage-blobs-cpp@12.18.0~shared+pic", type="build")
        depends_on("azure-storage-files-datalake-cpp@12.16.0~shared+pic", type="build")
        depends_on("libxml2~shared+pic", type="build")
    with when("link_dependencies=shared"):
        depends_on("azure-core-cpp@1.16.3+shared", type="link")
        depends_on("azure-identity-cpp@1.13.3+shared", type="link")
        depends_on("azure-storage-common-cpp@12.14.0+shared", type="link")
        depends_on("azure-storage-blobs-cpp@12.18.0+shared", type="link")
        depends_on("azure-storage-files-datalake-cpp@12.16.0+shared", type="link")
        depends_on("curl", type="link")
        depends_on("libiconv", type="link")
        depends_on("libxml2+shared", type="link")
        depends_on("zlib-api", type="link")

    published_binaries(
        "azure",
        "2.0.0",
        {
            "linux_amd64": "14007ba50d04e14e8e4dda3b808458ad8ca30a8d5e3a34c9434ec180c6fb4250",
            "linux_arm64": "9e10a7bef903e747fe92647ba804e6a37c5d82537ca44a8def499ffdc8bbca2b",
            "osx_amd64": "d695793f5c1e64376ce60f609b0dfbad88a8de73071f91ba88aeb64c1b19f265",
            "osx_arm64": "0ba14c30bf590d38a20b2e3849fda45bbd7572565afa315582feddd3c4c38452",
        },
    )

    resource(
        name="extension_source",
        git="https://github.com/duckdb/duckdb-azure.git",
        commit="906e92458c33309e5d9413e14a85aad7b4d2275f",
        placement="extension_source",
        when="@2.0.0 ~prebuilt",
    )
