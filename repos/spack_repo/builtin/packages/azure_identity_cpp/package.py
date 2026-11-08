# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage

from spack.package import *


class AzureIdentityCpp(CMakePackage):
    """Azure Identity SDK for C++: credentials that authenticate with Microsoft Entra ID
    for the Azure SDK client libraries for C++."""

    homepage = "https://github.com/Azure/azure-sdk-for-cpp/tree/main/sdk/identity/azure-identity"
    url = (
        "https://github.com/Azure/azure-sdk-for-cpp/archive/refs/tags/azure-identity_1.13.3.tar.gz"
    )
    git = "https://github.com/Azure/azure-sdk-for-cpp.git"

    maintainers("teaguesterling")

    license("MIT")

    version("1.13.3", sha256="4e83559e53b475e25f6a142604a477609b271111982bd2c88c8a4fe371338fcc")

    variant("shared", default=True, description="Build a shared library")
    variant("pic", default=True, description="Build position-independent code")

    depends_on("cxx", type="build")
    depends_on("cmake@3.13:", type="build")
    depends_on("azure-core-cpp@1.16.2:")
    depends_on("openssl")

    # The repository holds all the SDK libraries. Each one has its own CMake project.
    root_cmakelists_dir = "sdk/identity/azure-identity"

    def url_for_version(self, version):
        return (
            "https://github.com/Azure/azure-sdk-for-cpp/archive/refs/tags/"
            f"azure-identity_{version}.tar.gz"
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
            self.define("BUILD_SAMPLES", False),
            self.define("BUILD_PERFORMANCE_TESTS", False),
            self.define("WARNINGS_AS_ERRORS", False),
            # export(PACKAGE) otherwise records the build directory in ~/.cmake/packages
            self.define("CMAKE_EXPORT_NO_PACKAGE_REGISTRY", True),
        ]
