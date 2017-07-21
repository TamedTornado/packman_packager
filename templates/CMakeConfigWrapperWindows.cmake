# This script is a simple wrapper of this package, allowing us to put more than one bitness into a CMake package

# New bitness suffix
IF(CMAKE_SIZEOF_VOID_P EQUAL 8)
	SET(LIBPATH_SUFFIX "64")
ELSE()
	SET(LIBPATH_SUFFIX "32")
ENDIF()				

SET(DEPENDENCY_NAME "@{DEPENDENCY_NAME}")
SET(PLATFORM_NAME "@{PLATFORM_NAME}")


# Get the directory of this file and then go up a directory to it's parent
get_filename_component(BASE_DIRECTORY "${CMAKE_CURRENT_LIST_FILE}" PATH)
get_filename_component(BASE_DIRECTORY "${BASE_DIRECTORY}" PATH)

# Switch on static CRT or not as well

# Default to -md
SET(PLATFORM_DIR "${PLATFORM_NAME}${LIBPATH_SUFFIX}-md")

# This option is defined in NVidiaBuildOptions! 
IF(DEFINED USE_STATIC_WINCRT)
	IF(USE_STATIC_WINCRT)
		SET(PLATFORM_DIR "${PLATFORM_NAME}${LIBPATH_SUFFIX}-mt")
	ENDIF()
ENDIF()

INCLUDE("${BASE_DIRECTORY}/platforms/${PLATFORM_DIR}/cmake/${DEPENDENCY_NAME}-config.cmake")

