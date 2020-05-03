
find_path(CyrusSASL_INCLUDE_DIR
    NAMES sasl/sasl.h
    PATHS ${CONAN_INCLUDE_DIRS_CYRUS_SASL}
    NO_DEFAULT_PATH
)

find_library(CyrusSASL_LIBRARY
    NAMES sasl2
    PATHS ${CONAN_LIB_DIRS_CYRUS_SASL}
    NO_DEFAULT_PATH
)

if(CyrusSASL_INCLUDE_DIR AND EXISTS ${CyrusSASL_INCLUDE_DIR}/sasl/sasl.h)

    file(STRINGS ${CyrusSASL_INCLUDE_DIR}/sasl/sasl.h DEFINE_CYRUS_SASL_MAJOR REGEX "^#define SASL_VERSION_MAJOR")
    string(REGEX REPLACE "^.*VERSION_MAJOR +([0-9]+).*$" "\\1" CyrusSASL_VERSION_MAJOR "${DEFINE_CYRUS_SASL_MAJOR}")

    file(STRINGS ${CyrusSASL_INCLUDE_DIR}/sasl/sasl.h DEFINE_CYRUS_SASL_MINOR REGEX "^#define SASL_VERSION_MINOR")
    string(REGEX REPLACE "^.*VERSION_MINOR +([0-9]+).*$" "\\1" CyrusSASL_VERSION_MINOR "${DEFINE_CYRUS_SASL_MINOR}")

    file(STRINGS ${CyrusSASL_INCLUDE_DIR}/sasl/sasl.h DEFINE_CYRUS_SASL_STEP REGEX "^#define SASL_VERSION_STEP")
    string(REGEX REPLACE "^.*VERSION_STEP +([0-9]+).*$" "\\1" CyrusSASL_VERSION_STEP "${DEFINE_CYRUS_SASL_STEP}")

    unset(DEFINE_CYRUS_SASL_MAJOR)
    unset(DEFINE_CYRUS_SASL_MINOR)
    unset(DEFINE_CYRUS_SASL_STEP)
    
    set(CyrusSASL_VERSION_STRING "${CyrusSASL_VERSION_MAJOR}.${CyrusSASL_VERSION_MINOR}.${CyrusSASL_VERSION_STEP}")
    set(CyrusSASL_VERSION ${CyrusSASL_VERSION_STRING})
    set(CyrusSASL_VERSION_COUNT 3)

    mark_as_advanced(CyrusSASL_VERSION_STRING CyrusSASL_VERSION CyrusSASL_VERSION_COUNT)
endif()

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(CyrusSASL
    REQUIRED_VARS
      CyrusSASL_INCLUDE_DIR
      CyrusSASL_LIBRARY
    VERSION_VAR
      CyrusSASL_VERSION
)

if(CyrusSASL_FOUND AND NOT TARGET CyrusSASL::CyrusSASL)

    add_library(CyrusSASL::CyrusSASL UNKNOWN IMPORTED)
    set_target_properties(CyrusSASL::CyrusSASL PROPERTIES
        IMPORTED_LOCATION ${CyrusSASL_LIBRARY}
        INTERFACE_INCLUDE_DIRECTORIES ${CyrusSASL_INCLUDE_DIR}
        INTERFACE_COMPILE_DEFINITIONS "${CONAN_COMPILE_DEFINITIONS_CYRUS_SASL}"
    )

    mark_as_advanced(CyrusSASL_INCLUDE_DIR CyrusSASL_LIBRARY)

    set(CyrusSASL_INCLUDE_DIRS ${CyrusSASL_INCLUDE_DIR})
    set(CyrusSASL_LIBRARIES ${CyrusSASL_LIBRARY})
    set(CyrusSASL_DEFINITIONS "${CONAN_COMPILE_DEFINITIONS_CYRUS_SASL}")

endif()

