# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage

from spack.package import *


class AzureStorageCommonCpp(CMakePackage):
    """Azure Storage Common SDK for C++: the abstractions that the Azure Storage client
    libraries for C++ share."""

    homepage = (
        "https://github.com/Azure/azure-sdk-for-cpp/tree/main/sdk/storage/azure-storage-common"
    )
    url = (
        "https://github.com/Azure/azure-sdk-for-cpp/archive/refs/tags/"
        "azure-storage-common_12.14.0.tar.gz"
    )
    git = "https://github.com/Azure/azure-sdk-for-cpp.git"

    maintainers("teaguesterling")

    license("MIT")

    version("12.15.0", sha256="23a10c84418f6d8c07858277f3b8e7c7344008f1ab9eacabdc485fb0744903e5")
    version("12.14.0", sha256="68b3d88d5f1358b3607b4fb76674373c91e1dd840920de05e5a82cf09fcc6e5b")

    variant("shared", default=True, description="Build a shared library")
    variant("pic", default=True, description="Build position-independent code")

    depends_on("cxx", type="build")
    depends_on("cmake@3.13:", type="build")
    depends_on("azure-core-cpp@1.16.3:")
    # storage_retry_policy.hpp of 12.15.0 does not compile with 1.16.3
    depends_on("azure-core-cpp@1.16.4:", when="@12.15.0:")
    depends_on("libxml2")
    depends_on("openssl")

    # The patch of the DuckDB overlay port for this version. 12.15.0 has the include.
    patch("add-cstdint-include.patch", when="@12.14.0")

    # The repository holds all the SDK libraries. Each one has its own CMake project.
    root_cmakelists_dir = "sdk/storage/azure-storage-common"

    def url_for_version(self, version):
        return (
            "https://github.com/Azure/azure-sdk-for-cpp/archive/refs/tags/"
            f"azure-storage-common_{version}.tar.gz"
        )

    def setup_build_environment(self, env: EnvironmentModifications) -> None:
        # Otherwise CMake clones vcpkg with FetchContent, and uses it as the toolchain
        env.set("AZURE_SDK_DISABLE_AUTO_VCPKG", "1")

    def cmake_args(self):
        return [
            self.define_from_variant("BUILD_SHARED_LIBS", "shared"),
            self.define_from_variant("CMAKE_POSITION_INDEPENDENT_CODE", "pic"),
            # Use the installed azure-core-cpp, not a copy that CMake downloads
            self.define("FETCH_SOURCE_DEPS", False),
            # The tests download GoogleTest with FetchContent
            self.define("BUILD_TESTING", False),
            self.define("WARNINGS_AS_ERRORS", False),
            # export(PACKAGE) otherwise records the build directory in ~/.cmake/packages
            self.define("CMAKE_EXPORT_NO_PACKAGE_REGISTRY", True),
        ]
