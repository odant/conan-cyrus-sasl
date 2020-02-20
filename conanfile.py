from conans import ConanFile, CMake, AutoToolsBuildEnvironment, tools
from conans.errors import ConanException
import os, glob, shutil


def get_safe(options, name):
    try:
        return getattr(options, name, None)
    except ConanException:
        return None


class CyrusSaslConan(ConanFile):
    name = "cyrus-sasl"
    version = "2.1.26+0"
    license = "Apache License v2.0"
    description = "Cyrus SASL C++ library"
    url = "https://github.com/cyrusimap/cyrus-sasl"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "dll_sign": [True, False],
        "ninja": [False, True],
        "shared": [True, False],
        "plugins_shared": [True, False]
    }
    default_options = "dll_sign=True", "ninja=True", "shared=True", "plugins_shared=False"
    generators = "cmake"
    exports_sources = "src/*", "cyrus-sasl-2.1.26.patch", "cyrus-sasl-2.1.26-fixes-3.patch", "cyrus-sasl-2.1.26-openssl-1.1.0-1.patch", "Findcyrus-sasl.cmake", "CMakeLists.txt"
    no_copy_source = True
    build_policy = "missing"
    # define openssl version
    _openssl_version = "1.1.0l+2"
    
    def configure(self):
        if self.settings.compiler.get_safe("libcxx") == "libstdc++":
            raise Exception("This package is only compatible with libstdc++11")
        # MT(d) static library
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            if self.settings.compiler.runtime == "MT" or self.settings.compiler.runtime == "MTd":
                self.options.shared=False
        # DLL sign, only Windows and shared
        if self.settings.os != "Windows" or self.options.shared == False:
            del self.options.dll_sign

    def build_requirements(self):
        if get_safe(self.options, "ninja"):
            self.build_requires("ninja_installer/1.9.0@bincrafters/stable")
        if get_safe(self.options, "dll_sign"):
            self.build_requires("windows_signtool/[>=1.1]@%s/stable" % self.user)

    def requirements(self):
        self.requires("openssl/%s@%s/stable" % (self._openssl_version, self.user))
        
    def source(self):
        tools.patch(patch_file="cyrus-sasl-2.1.26-fixes-3.patch")
        tools.patch(patch_file="cyrus-sasl-2.1.26-openssl-1.1.0-1.patch")
        tools.patch(patch_file="cyrus-sasl-2.1.26.patch")

    def build_cmake(self):
        build_type = "RelWithDebInfo" if self.settings.build_type == "Release" else "Debug"
        generator = "Ninja" if self.options.ninja == True else None
        cmake = CMake(self, build_type=build_type, generator=generator)
        cmake.verbose = False
        if self.options.shared:
            cmake.definitions["STATIC_LIBRARY:BOOL"] = "OFF"
        if self.options.plugins_shared:
            cmake.definitions["STATIC_PLUGIN:BOOL"] = "OFF"
        cmake.configure()
        cmake.build()
        cmake.install()

    def build_autotools(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure()
        autotools.make()
        
    def build(self):
        self.build_cmake()

    def package_id(self):
        self.info.options.ninja = "any"

    def sign_binary(self, path):
        import windows_signtool
        for fpath in glob.glob(path):
            fpath = fpath.replace("\\", "/")
            for alg in ["sha1", "sha256"]:
                is_timestamp = True if self.settings.build_type == "Release" else False
                cmd = windows_signtool.get_sign_command(fpath, digest_algorithm=alg, timestamp=is_timestamp)
                self.output.info("Sign %s" % fpath)
                self.run(cmd)
        
    def package(self):
        self.copy("Findcyrus-sasl.cmake", dst=".", src=".", keep_path=False)
        self.copy("config.h", dst="include/sasl", src="./src", keep_path=False)
        # Sign DLL
        if get_safe(self.options, "dll_sign"):
            bin_path = os.path.join(self.package_folder, "bin")
            lib_binary = os.path.join(bin_path, "*.dll")
            self.sign_binary(lib_binary)
            plugin_binaries = os.path.join(bin_path, "sasl2", "*.dll")
            self.sign_binary(plugin_binaries)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
