from conan import ConanFile, tools
import os, glob


class CyrusSaslConan(ConanFile):
    name = "cyrus-sasl"
    version = "2.1.26+10"
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
    default_options = { 
        "dll_sign": True, 
        "ninja":    True, 
        "shared":   True, 
        "plugins_shared": False
    }
    exports_sources = "src/*", "cyrus-sasl-2.1.26.patch", "cyrus-sasl-2.1.26-fixes-3.patch", "cyrus-sasl-2.1.26-openssl-1.1.0-1.patch", "fix_saslint.h.patch"
    no_copy_source = True
    build_policy = "missing"
    package_type = "library"
    python_requires = "windows_signtool/[>=1.2]@odant/stable"
    
    def layout(self):
        tools.cmake.cmake_layout(self, src_folder="src")

    def configure(self):
        if self.settings.compiler.get_safe("libcxx") == "libstdc++":
            raise Exception("This package is only compatible with libstdc++11")
        # MT(d) static library
        if self.settings.os == "Windows" and (self.settings.compiler == "msvc" or ( self.settings.compiler == "clang" and self.settings.compiler.get_safe("runtime_version"))):
            if self.settings.compiler.runtime == "static":
                self.options.shared=False
        # DLL sign, only Windows and shared
        if self.settings.os != "Windows" or self.options.shared == False:
            self.options.rm_safe("dll_sign")

    def build_requirements(self):
        if self.options.get_safe("ninja"):
            self.build_requires("ninja/[>=1.12.1]")

    def requirements(self):
        self.requires("openssl/[>=3.0.16]@%s/stable" % self.user)

    def source(self):
        tools.files.patch(self, patch_file="cyrus-sasl-2.1.26-fixes-3.patch")
        tools.files.patch(self, patch_file="cyrus-sasl-2.1.26-openssl-1.1.0-1.patch")
        tools.files.patch(self, patch_file="cyrus-sasl-2.1.26.patch")
        tools.files.patch(self, patch_file="fix_saslint.h.patch")
        
    def generate(self):
        benv = tools.env.VirtualBuildEnv(self)
        benv.generate()
        renv = tools.env.VirtualRunEnv(self)
        renv.generate()
        if self.settings.os == "Windows" and (self.settings.compiler == "msvc" or ( self.settings.compiler == "clang" and self.settings.compiler.get_safe("runtime_version"))):
            vc = tools.microsoft.VCVars(self)
            vc.generate()
        deps = tools.cmake.CMakeDeps(self)    
        deps.generate()
        cmakeGenerator = "Ninja" if self.options.ninja else None
        tc = tools.cmake.CMakeToolchain(self, generator=cmakeGenerator)
        tc.preprocessor_definitions["PROTOTYPES"] = "1"
        if self.options.shared:
            tc.variables["STATIC_LIBRARY"] = "OFF"
        if self.options.plugins_shared:
            tc.variables["STATIC_PLUGIN"] = "OFF"
        if self.settings.compiler == "gcc" or self.settings.compiler == "clang":
            tc.extra_cflags.append("-Wno-error=implicit-function-declaration")
            tc.extra_cflags.append("-Wno-error=incompatible-pointer-types")
        tc.generate()

    def build(self):
        cmake = tools.cmake.CMake(self)
        cmake.configure()
        cmake.build()

    def package_id(self):
        self.info.options.ninja = "any"

    def package(self):
        cmake = tools.cmake.CMake(self)
        cmake.install()
        tools.files.copy(self, "config.h", dst=os.path.join(self.package_folder, "include", "sasl"), src=self.build_folder, keep_path=False)
        # Sign DLL
        if self.options.get_safe("dll_sign"):
            self.python_requires["windows_signtool"].module.sign(self, [os.path.join(self.package_folder, "bin", "*.dll")])

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "CyrusSASL")
        self.cpp_info.set_property("cmake_target_name", "CyrusSASL::CyrusSASL")
        self.cpp_info.libs = tools.files.collect_libs(self)
