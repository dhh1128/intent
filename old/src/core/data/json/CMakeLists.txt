cmake_minimum_required(VERSION 2.8)

OPTION(JSONCPP_LIB_BUILD_SHARED "Build jsoncpp_lib as a shared library." OFF)
OPTION(JSONCPP_LIB_BUILD_STATIC "Build jsoncpp_lib static library." ON)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Werror=strict-aliasing")

IF(BUILD_SHARED_LIBS)
  SET(JSONCPP_LIB_BUILD_SHARED ON)
ENDIF(BUILD_SHARED_LIBS)

SET( PUBLIC_HEADERS
    config.h
    forwards.h
    features.h
    value.h
    reader.h
    writer.h
    assertions.h
    version.h
    )

SOURCE_GROUP( "Public API" FILES ${PUBLIC_HEADERS} )

SET(jsoncpp_sources
                tool.h
                reader.cpp
                value_iterator.inl
                value.cpp
                writer.cpp
                version.h.in)

# Install instructions for this target
IF(JSONCPP_WITH_CMAKE_PACKAGE)
    SET(INSTALL_EXPORT EXPORT jsoncpp)
ELSE()
    SET(INSTALL_EXPORT)
ENDIF()

IF(JSONCPP_LIB_BUILD_SHARED)
    ADD_DEFINITIONS( -DJSON_DLL_BUILD )
    ADD_LIBRARY(jsoncpp_lib SHARED ${PUBLIC_HEADERS} ${jsoncpp_sources})
    SET_TARGET_PROPERTIES( jsoncpp_lib PROPERTIES VERSION ${JSONCPP_VERSION} SOVERSION ${JSONCPP_VERSION_MAJOR})
    SET_TARGET_PROPERTIES( jsoncpp_lib PROPERTIES OUTPUT_NAME jsoncpp )

    INSTALL( TARGETS jsoncpp_lib ${INSTALL_EXPORT}
         RUNTIME DESTINATION ${RUNTIME_INSTALL_DIR}
         LIBRARY DESTINATION ${LIBRARY_INSTALL_DIR}
         ARCHIVE DESTINATION ${ARCHIVE_INSTALL_DIR})

    IF(NOT CMAKE_VERSION VERSION_LESS 2.8.11)
        TARGET_INCLUDE_DIRECTORIES( jsoncpp_lib PUBLIC
                                   $<INSTALL_INTERFACE:${INCLUDE_INSTALL_DIR}>
                                   $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/${JSONCPP_INCLUDE_DIR}>)
    ENDIF(NOT CMAKE_VERSION VERSION_LESS 2.8.11)

ENDIF()

IF(JSONCPP_LIB_BUILD_STATIC)
    ADD_LIBRARY(jsoncpp_lib_static STATIC ${PUBLIC_HEADERS} ${jsoncpp_sources})
    SET_TARGET_PROPERTIES( jsoncpp_lib_static PROPERTIES VERSION ${JSONCPP_VERSION} SOVERSION ${JSONCPP_VERSION_MAJOR})
    SET_TARGET_PROPERTIES( jsoncpp_lib_static PROPERTIES OUTPUT_NAME jsoncpp )

if(0)
    INSTALL( TARGETS jsoncpp_lib_static ${INSTALL_EXPORT}
         RUNTIME DESTINATION ${RUNTIME_INSTALL_DIR}
         LIBRARY DESTINATION ${LIBRARY_INSTALL_DIR}
             ARCHIVE DESTINATION ${ARCHIVE_INSTALL_DIR})
endif()

    IF(NOT CMAKE_VERSION VERSION_LESS 2.8.11)
        TARGET_INCLUDE_DIRECTORIES( jsoncpp_lib_static PUBLIC
                                $<INSTALL_INTERFACE:${INCLUDE_INSTALL_DIR}>
                                $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/${JSONCPP_INCLUDE_DIR}>
                                )
     ENDIF(NOT CMAKE_VERSION VERSION_LESS 2.8.11)

ENDIF()
