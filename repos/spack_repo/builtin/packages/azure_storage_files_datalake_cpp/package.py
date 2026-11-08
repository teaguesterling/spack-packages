# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage

from spack.package import *


class AzureStorageFilesDatalakeCpp(CMakePackage):
    """Azure Storage Files Data Lake SDK for C++: a client library for Azure Data Lake
    Storage Gen2."""

    homepage = (
        "https://github.com/Azure/azure-sdk-for-cpp/tree/main/sdk/storage/"
        "azure-storage-files-datalake"
    )
    url = (
        "https://github.com/Azure/azure-sdk-for-cpp/archive/refs/tags/"
        "azure-storage-files-datalake_12.16.0.tar.gz"
    )
    git = "https://github.com/Azure/azure-sdk-for-cpp.git"

    maintainers("teaguesterling")

    license("MIT")

    version("12.16.0", sha256="9da06bb9ceddd11f63a8d8f0dceefe9fe4ec8f826544c3cbf358a59be93d9f92")

    variant("shared", default=True, description="Build a shared library")
    variant("pic", default=True, description="Build position-independent code")

    depends_on("cxx", type="build")
    depends_on("cmake@3.13:", type="build")
    depends_on("azure-storage-blobs-cpp@12.18.0:")

    # The repository holds all the SDK libraries. Each one has its own CMake project.
    root_cmakelists_dir = "sdk/storage/azure-storage-files-datalake"

    def url_for_version(self, version):
        return (
            "https://github.com/Azure/azure-sdk-for-cpp/archive/refs/tags/"
            f"azure-storage-files-datalake_{version}.tar.gz"
        )

    def setup_build_environment(self, env: EnvironmentModifications) -> None:
        # Otherwise CMake clones vcpkg with FetchContent, and uses it as the toolchain
        env.set("AZURE_SDK_DISABLE_AUTO_VCPKG", "1")

    def cmake_args(self):
        return [
            self.define_from_variant("BUILD_SHARED_LIBS", "shared"),
            self.define_from_variant("CMAKE_POSITION_INDEPENDENT_CODE", "pic"),
            # Use the installed azure-storage-blobs-cpp, not a copy that CMake downloads
            self.define("FETCH_SOURCE_DEPS", False),
            # The tests download GoogleTest with FetchContent
            self.define("BUILD_TESTING", False),
            self.define("BUILD_SAMPLES", False),
            self.define("WARNINGS_AS_ERRORS", False),
            # export(PACKAGE) otherwise records the build directory in ~/.cmake/packages
            self.define("CMAKE_EXPORT_NO_PACKAGE_REGISTRY", True),
        ]
