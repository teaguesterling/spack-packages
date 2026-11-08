# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.packages.duckdb_extensions.package import (
    DuckdbCommunityExtensionPackage,
    published_binaries,
)

from spack.package import *


class DuckdbMssql(DuckdbCommunityExtensionPackage):
    """Adds support for connecting to Microsoft SQL Server."""

    homepage = "https://github.com/hugr-lab/mssql-extension"

    license("MIT")

    with when("~prebuilt"):
        # Kerberos needs only the headers: the extension opens the library with dlopen
        depends_on("krb5", type="build")
        depends_on("pkgconfig", type="build")
        # FindOpenSSL asks for ZLIB::ZLIB, because the static OpenSSL of Spack uses zlib
        depends_on("zlib-api", type="build")
    with when("link_dependencies=static"):
        # The version that vcpkg.json of the extension pins
        depends_on("simdutf@6.1.1~shared+pic", type="build")
    with when("link_dependencies=shared"):
        depends_on("simdutf@6.1.1+shared", type="link")
        depends_on("zlib-api", type="link")

    published_binaries(
        "mssql",
        "2.0.0",
        {
            "linux_amd64": "556e08a5c8c969b0325e1d7dd929309f66954789ad5af624ac0b557cf6ce7ea5",
            "linux_arm64": "15042f71d858844ad20daff0cc36b5c33f264e070b5da575117bfcded7372e9d",
            "osx_arm64": "5f0361a61f0aea8f0f57c4a937782ad6afbbb711fca908d5a7be72ba77276ca5",
        },
        repository="community",
    )

    resource(
        name="extension_source",
        git="https://github.com/hugr-lab/mssql-extension.git",
        commit="bfd347ffa89dc520eb0fb82c857b3c7af12673dc",
        placement="extension_source",
        when="@2.0.0 ~prebuilt",
    )
