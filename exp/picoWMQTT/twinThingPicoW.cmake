# Add library cpp files
#set(FREERTOS_PORT_PATH      ${TWIN_THING_PATH}/lib/twinThingPicoESP/port/FreeRTOS)

if (NOT DEFINED TWIN_THING_PATH)
 set(TWIN_THING_PATH "${TWIN_THING_PATH}/lib/twinThingPico1-2W")
endif()

add_library(twinThingPicoW INTERFACE)
target_sources(twinThingPicoW INTERFACE
    ${TWIN_THING_PATH}/src/MQTTAgent.cpp
    #${TWIN_THING_PATH}/src/WifiHelper.cpp
    
    ${TWIN_THING_PATH}/src/MQTTInterface.cpp
    ${TWIN_THING_PATH}/src/MQTTRouter.cpp
    ${TWIN_THING_PATH}/src/MQTTRouterPing.cpp
    ${TWIN_THING_PATH}/src/MQTTPingTask.cpp
    ${TWIN_THING_PATH}/src/MQTTTopicHelper.cpp
    ${TWIN_THING_PATH}/src/State.cpp
    ${TWIN_THING_PATH}/src/StateObserver.cpp
    ${TWIN_THING_PATH}/src/StateTemp.cpp
    ${TWIN_THING_PATH}/src/TwinTask.cpp
    ${TWIN_THING_PATH}/src/MQTTRouterTwin.cpp
	${TWIN_THING_PATH}/src/MQTTAgentObserver.cpp
	
	${TWIN_THING_PATH}/src/TCPTransport.cpp
	${TWIN_THING_PATH}/src/Transport.cpp
)

# Add include directory
target_include_directories(twinThingPicoW INTERFACE 
	${TWIN_THING_PATH}/src
	${TWIN_THING_PICO_CONFIG_PATH}
)

# Add the standard library to the build
target_link_libraries(twinThingPicoW INTERFACE 
	pico_stdlib 
	pico_unique_id
	hardware_adc
	hardware_rtc
	json_maker 
	tiny_json
	FreeRTOS-Kernel
	coreMQTT 
	coreMQTTAgent
	)

