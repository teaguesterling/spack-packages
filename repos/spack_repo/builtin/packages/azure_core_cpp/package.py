# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage

from spack.package import *


class AzureCoreCpp(CMakePackage):
    """Azure Core SDK for C++: the shared primitives, abstractions and helpers of the Azure
    SDK client libraries for C++. On Linux, the HTTP transport uses libcurl."""

    homepage = "https://github.com/Azure/azure-sdk-for-cpp/tree/main/sdk/core/azure-core"
    url = "https://github.com/Azure/azure-sdk-for-cpp/archive/refs/tags/azure-core_1.16.3.tar.gz"
    git = "https://github.com/Azure/azure-sdk-for-cpp.git"

    maintainers("teaguesterling")

    license("MIT")

    version("1.16.4", sha256="25f8badf23c66ae82debd95e0d074d6269b276e5fa2ce5d4d3cff38fda9ab8c2")
    version("1.16.3", sha256="70d5d2aea5ece95148ee8b71fb302ae35a1178e58b58150a14df8866a0c54464")

    variant("shared", default=True, description="Build a shared library")
    variant("pic", default=True, description="Build position-independent code")

    depends_on("cxx", type="build")
    depends_on("cmake@3.13:", type="build")
    depends_on("curl")
    depends_on("openssl")
    # src/http/curl/curl.cpp passes the const X509_NAME of OpenSSL 4 as X509_NAME*. 1.16.4
    # has the same file as 1.16.3, which fails to compile.
    depends_on("openssl@:3", when="@:1.16.4")

    # The repository holds all the SDK libraries. Each one has its own CMake project.
    root_cmakelists_dir = "sdk/core/azure-core"

    def url_for_version(self, version):
        return (
            "https://github.com/Azure/azure-sdk-for-cpp/archive/refs/tags/"
            f"azure-core_{version}.tar.gz"
        )

    def setup_build_environment(self, env: EnvironmentModifications) -> None:
        # Otherwise CMake clones vcpkg with FetchContent, and uses it as the toolchain
        env.set("AZURE_SDK_DISABLE_AUTO_VCPKG", "1")

    def cmake_args(self):
        return [
            self.define_from_variant("BUILD_SHARED_LIBS", "shared"),
            self.define_from_variant("CMAKE_POSITION_INDEPENDENT_CODE", "pic"),
            self.define("BUILD_TRANSPORT_CURL", True),
            # The tests download GoogleTest with FetchContent
            self.define("BUILD_TESTING", False),
            self.define("BUILD_PERFORMANCE_TESTS", False),
            self.define("WARNINGS_AS_ERRORS", False),
            # export(PACKAGE) otherwise records the build directory in ~/.cmake/packages
            self.define("CMAKE_EXPORT_NO_PACKAGE_REGISTRY", True),
        ]
