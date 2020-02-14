include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(OpenSSL REQUIRED)

add_subdirectory(src)
