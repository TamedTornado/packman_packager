# This script is a simple wrapper of this package, allowing us to put more than one bitness into a CMake package

# Determine the bitness of the compiler
IF(FORCE_32BIT_SUFFIX AND FORCE_64BIT_SUFFIX)
	MESSAGE(FATAL_ERROR "Cannot specify both FORCE_64BIT_SUFFIX and FORCE_32BIT_SUFFIX. Choose one.")
ENDIF()

IF (FORCE_32BIT_SUFFIX)
	MESSAGE("Forcing binary suffixes to 32 bit.")
	SET(LIBPATH_SUFFIX "32")
	# Set default exe suffix. Unset on platforms that don't need it. Include underscore since it's optional
	SET(EXE_SUFFIX "_32")
ELSEIF(FORCE_64BIT_SUFFIX)
	MESSAGE("Forcing binary suffixes to 64 bit.")
	SET(LIBPATH_SUFFIX "64")
	# Set default exe suffix. Unset on platforms that don't need it. Include underscore since it's optional
	SET(EXE_SUFFIX "_64")
ELSE()
	# New bitness suffix
	IF(CMAKE_SIZEOF_VOID_P EQUAL 8)
		SET(LIBPATH_SUFFIX "64")
		# Set default exe suffix. Unset on platforms that don't need it. Include underscore since it's optional
		SET(EXE_SUFFIX "_64")
	ELSE()
		SET(LIBPATH_SUFFIX "32")
		# Set default exe suffix. Unset on platforms that don't need it. Include underscore since it's optional
		SET(EXE_SUFFIX "_32")
	ENDIF()
ENDIF()

SET(DEPENDENCY_NAME "@{DEPENDENCY_NAME}")
SET(PLATFORM_NAME "@{PLATFORM_NAME}")

# Get the directory of this file and then go up a directory to it's parent
get_filename_component(BASE_DIRECTORY "${CMAKE_CURRENT_LIST_FILE}" PATH)
get_filename_component(BASE_DIRECTORY "${BASE_DIRECTORY}" PATH)

# There's no other platform switching to do on *NIX - just 32 or 64 bit.
SET(PLATFORM_DIR "${PLATFORM_NAME}${LIBPATH_SUFFIX}")

INCLUDE("${BASE_DIRECTORY}/platforms/${PLATFORM_DIR}/cmake/${DEPENDENCY_NAME}-config.cmake")

