# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage

from spack.package import *


class AwsSdkCpp(CMakePackage):
    """AWS SDK for C++.

    The AWS SDK for C++ provides a modern C++ (version C++ 11 or later) interface for
    Amazon Web Services (AWS). It is meant to be performant and fully functioning with
    low- and high-level SDKs, while minimizing dependencies and providing platform
    portability (Windows, OSX, Linux, and mobile).
    """

    homepage = "https://github.com/aws/aws-sdk-cpp"
    git = "https://github.com/aws/aws-sdk-cpp.git"

    license("Apache-2.0")

    version(
        "1.11.820",
        tag="1.11.820",
        commit="58442a4d2516aa235f86527b39ec60cf72cfc818",
        submodules=True,
    )
    version(
        "1.11.144",
        tag="1.11.144",
        commit="498339d47146f8e3ee9ae0fad3fcda5acbaea1e6",
        submodules=True,
    )
    version(
        "1.10.57",
        tag="1.10.57",
        commit="777e0dd4b90eda8bf65bc4b5fce2f90febdbd2b8",
        submodules=True,
    )
    version(
        "1.10.32",
        tag="1.10.32",
        commit="40594bc05a3f68fe14f2f1a54c5c3e6752b1e290",
        submodules=True,
    )
    version(
        "1.9.379",
        tag="1.9.379",
        commit="94d02db44730b0a5cef98ce33deedf43f5333700",
        submodules=True,
    )
    version(
        "1.9.247",
        tag="1.9.247",
        commit="4bf33aa0172704eb5fc1da8086686670711bd801",
        submodules=True,
    )

    variant(
        "components",
        default="s3,transfer",
        values=(
            "cloudformation",
            "cognito-identity",
            "iam",
            "identity-management",
            "rds",
            "redshift",
            "redshift-serverless",
            "s3",
            "sso",
            "sts",
            "transfer",
        ),
        multi=True,
        description="Service and high-level libraries to build (BUILD_ONLY); core is always built",
    )
    variant(
        "shared",
        default=True,
        description="Build shared libraries; otherwise build static libraries with PIC",
    )

    conflicts("components=redshift-serverless", when="@:1.9")

    depends_on("c", type="build")  # generated
    depends_on("cxx", type="build")  # generated

    depends_on("cmake@3.1:", type="build")
    depends_on("zlib-api")
    depends_on("curl")
    # The SDK and the libcrypto backend of its common runtime (s2n, aws-c-cal) find OpenSSL.
    # The s2n of 1.11.820 does not compile with OpenSSL 4, where ASN1_STRING is opaque.
    # Older versions were not built with OpenSSL 4, so they keep no upper bound.
    depends_on("openssl", when="platform=linux")
    depends_on("openssl@:3", when="@1.11.820 platform=linux")

    # The backport that the DuckDB vcpkg registry applies to this version:
    # https://github.com/aws/aws-sdk-cpp/pull/3922
    patch("fix-crt-credentials-expiration.patch", when="@1.11.820")

    # https://github.com/aws/aws-sdk-cpp/issues/1816
    patch(
        "https://github.com/aws/aws-sdk-cpp/pull/1937.patch?full_index=1",
        sha256="ba86e0556322604fb4b70e2dd4f4fb874701868b07353fc1d5c329d90777bf45",
        when="@1.9.247",
    )

    def cmake_args(self):
        args = [
            self.define("BUILD_ONLY", self.spec.variants["components"].value),
            self.define("ENABLE_TESTING", False),
            self.define("AUTORUN_UNIT_TESTS", False),
        ]
        if self.spec.satisfies("~shared"):
            args += [
                self.define("BUILD_SHARED_LIBS", False),
                self.define("CMAKE_POSITION_INDEPENDENT_CODE", True),
                # As the vcpkg port does: a new compiler warning must not fail this build
                self.define("AWS_SDK_WARNINGS_ARE_ERRORS", False),
                # The CMake config of a static SDK names the libraries that it links. A
                # static library there lets a consumer link with no shared dependencies.
                self.define("OPENSSL_USE_STATIC_LIBS", True),
                self.define("ZLIB_USE_STATIC_LIBS", True),
            ]
            curl = find_libraries(
                "libcurl", self.spec["curl"].prefix, shared=False, recursive=True
            )
            if not curl:
                raise InstallError("~shared needs the static library of curl (curl libs=static)")
            args.append(self.define("CURL_LIBRARY", curl[0]))
        return args
