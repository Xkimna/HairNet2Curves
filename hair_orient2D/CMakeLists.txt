cmake_minimum_required(VERSION 3.8)
project(Orient2D)

set(CMAKE_CXX_STANDARD 11)

#file(GLOB *.h *.cpp)

set(SOURCE_FILES main_nobody.cpp Color.h Im.hpp lineqn.h MathUtils.hpp Orient2D.hpp OrientMap.hpp
        util.h Vec.hpp XForm.h Renderer.h SimpleFragmentShader.fragmentshader SimpleVertexShader.vertexshader
        )
set(OpenCV_DIR D:\\libraries\\opencv\\build)
find_package(OpenCV REQUIRED)
find_package(OpenMP)
if (OPENMP_FOUND)
    set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
    set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
endif()
FIND_PACKAGE(JPEG REQUIRED)
FIND_PACKAGE(PNG  REQUIRED)


INCLUDE_DIRECTORIES(${PROJECT_SOURCE_DIR}/include
				${JPEG_INCLUDE_DIR}
                    ${PNG_INCLUDE_DIR}
                    ${OpenCV_INCLUDE_DIRS}
                    )

link_directories(${PROJECT_SOURCE_DIR}/lib) 
add_executable(Orient2D ${SOURCE_FILES} )

target_link_libraries(Orient2D
        ${OpenCV_LIBS}
        ${JPEG_LIBRARIES}
        ${PNG_LIBRARIES}
libfftw3-3 libfftw3f-3 libfftw3l-3
        )
