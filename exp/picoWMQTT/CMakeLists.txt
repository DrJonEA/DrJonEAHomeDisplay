cmake_minimum_required(VERSION 3.12)

# Change your executable name to something creative!
set(NAME Twin) # <-- Name your project/executable here!

set(PICO_BOARD pico_w)

include("$ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake")

# Gooey boilerplate
project(${NAME} C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(PICO_CXX_ENABLE_EXCEPTIONS 1)

# Initialize the SDK
pico_sdk_init()

set(LIB_FOLDER "${CMAKE_CURRENT_LIST_DIR}/../../lib/")

set(TWIN_THING_PICO_CONFIG_PATH ${CMAKE_CURRENT_LIST_DIR}/port/twinThing)
set(COREMQTT_PORT_PATH      ${CMAKE_CURRENT_LIST_DIR}/port/CoreMQTT)
set(COREMQTT_AGENT_PORT_PATH      ${CMAKE_CURRENT_LIST_DIR}/port/CoreMQTT-Agent)


include(lwip_import.cmake)

SET(FREERTOS_KERNEL_PATH "${LIB_FOLDER}/FreeRTOS-Kernel" CACHE STRING "Course Common Lib")
SET(FREERTOS_CONFIG_FILE_DIRECTORY "${CMAKE_CURRENT_LIST_DIR}/port/FreeRTOS-Kernel" CACHE STRING "Local Config")
include("${FREERTOS_CONFIG_FILE_DIRECTORY}/freertos_config.cmake") 
include(FreeRTOS_Kernel_import.cmake)

set(CORE_MQTT_DIR "${LIB_FOLDER}/coreMQTT" CACHE STRING "Course Common Lib")
include("FreeRTOS-coreMQTT.cmake")

set(CORE_MQTT_AGENT_DIR "${LIB_FOLDER}/coreMQTT-Agent" CACHE STRING "Course Common Lib")
include("FreeRTOS-coreMQTT-Agent.cmake")

set(TINY_JSON_DIR "${LIB_FOLDER}/tiny-json" CACHE STRING "Course Common Lib")
include("tiny-json.cmake")

set(JSON_MAKER_DIR "${LIB_FOLDER}/json-maker" CACHE STRING "Course Common Lib")
include("json-maker.cmake")

set(PIMORONI_DIR "${LIB_FOLDER}/pimoroni-pico")
include(cosmic_unicorn.cmake)

set(LVGL_DIR "${LIB_FOLDER}/lvgl")
include("lvgl.cmake")

set(COREHTTP_PATH "${LIB_FOLDER}/coreHTTP" CACHE STRING "Course Common Lib")
set(COREHTTP_PORT "${CMAKE_CURRENT_LIST_DIR}/port/coreHTTP/" CACHE STRING "Course Common Lib")
include(coreHTTP.cmake)

SET(URILIB_PATH "${LIB_FOLDER}/uri-library" CACHE STRING "Common Lib")
include(urilib.cmake)

set(WOLFSSL_DIR "${LIB_FOLDER}/wolfssl" CACHE STRING "Course Common Lib")
include("wolfssl_import.cmake")

set(PICOW_WSCLIENT_PATH "${LIB_FOLDER}/RPIPicoWWSClient" CACHE STRING "Course Common Lib")
include("PicoW_WSClient.cmake")

set(TWIN_THING_PATH "${LIB_FOLDER}/twinThingPico1-2W" CACHE STRING "Course Common Lib")
include("twinThingPicoW.cmake")


add_subdirectory(src)

add_compile_definitions(
	PICO_CXX_DISABLE_ALLOCATION_OVERRIDES=1
	)

#Set up files for the release packages
install(CODE "execute_process(COMMAND $ENV{HOME}/bin/picoDeploy.sh ${CMAKE_CURRENT_BINARY_DIR}/src/${NAME}.elf)")

# Set up files for the release packages
install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/src/${NAME}.uf2
    DESTINATION ${CMAKE_CURRENT_BINARY_DIR}
)

set(CPACK_INCLUDE_TOPLEVEL_DIRECTORY OFF)
set(CPACK_GENERATOR "ZIP" "TGZ")
include(CPack)
