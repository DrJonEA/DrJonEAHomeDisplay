add_executable(${NAME}
        main.cpp
        Agent.cpp
        DeviceState.cpp
        MQTTClientAgent.cpp
        SensorAgent.cpp
        )

# Pull in our pico_stdlib which pulls in commonly used features
target_link_libraries(${NAME}
	 pico_stdlib
	 pico_aon_timer
     FreeRTOS-Kernel-Heap4 # FreeRTOS kernel and dynamic heap
     freertos_config
     LWIP_PORT
     pico_cyw43_arch_lwip_sys_freertos
     sensors

     picow_wsclient
	 wolfmqtt
	 json_maker
	 tiny_json

	 hardware_watchdog

	 onboard_nvs
	)

target_include_directories(${NAME} PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}
    ${CMAKE_CURRENT_BINARY_DIR}
     )

# Broker CA certificate (PEM), embedded so the broker's TLS certificate can
# be verified. Default certs/mqtt_ca.pem, or set MQTT_CA_FILE to another path.
if (DEFINED ENV{MQTT_CA_FILE})
	set(MQTT_CA_FILE "$ENV{MQTT_CA_FILE}")
else()
	set(MQTT_CA_FILE "${CMAKE_CURRENT_LIST_DIR}/../certs/mqtt_ca.pem")
endif()
if (NOT EXISTS "${MQTT_CA_FILE}")
	message(FATAL_ERROR "Broker CA certificate not found at ${MQTT_CA_FILE}. "
		"Copy the CA PEM there or set the MQTT_CA_FILE environment variable")
endif()
file(READ "${MQTT_CA_FILE}" MQTT_CA_RAW)
string(FIND "${MQTT_CA_RAW}" "-----BEGIN CERTIFICATE-----" CA_POS)
if (CA_POS LESS 0)
	message(FATAL_ERROR "${MQTT_CA_FILE} does not contain a PEM certificate")
endif()
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${MQTT_CA_FILE}")
file(STRINGS "${MQTT_CA_FILE}" CA_LINES)
set(MQTT_CA_PEM "")
foreach(CA_LINE IN LISTS CA_LINES)
	string(STRIP "${CA_LINE}" CA_LINE)
	if (NOT CA_LINE STREQUAL "")
		string(APPEND MQTT_CA_PEM "\t\"${CA_LINE}\\n\"\n")
	endif()
endforeach()
configure_file(mqtt_ca.h.in ${CMAKE_CURRENT_BINARY_DIR}/mqtt_ca.h @ONLY)
message(STATUS "MQTT broker CA: ${MQTT_CA_FILE}")

if (NOT DEFINED ENV{WIFI_SSID})
	message(FATAL_ERROR "WIFI_SSID Environment variable not defined")
endif()
if (NOT DEFINED ENV{WIFI_PASSWORD})
	message(FATAL_ERROR "WIFI_PASSWORD Environment variable not defined")
endif()
if (NOT DEFINED ENV{MQTT_CLIENT})
	message(FATAL_ERROR "MQTT_CLIENT Environment variable not defined")
endif()
if (NOT DEFINED ENV{MQTT_USER})
	message(FATAL_ERROR "MQTT_USER Environment variable not defined")
endif()
if (NOT DEFINED ENV{MQTT_PASSWD})
	message(FATAL_ERROR "MQTT_PASSWD Environment variable not defined")
endif()
if (NOT DEFINED ENV{MQTT_HOST})
	message(FATAL_ERROR "MQTT_HOST Environment variable not defined")
endif()
if (NOT DEFINED ENV{MQTT_PORT})
	message(FATAL_ERROR "MQTT_PORT Environment variable not defined")
endif()

target_compile_definitions(${NAME} PRIVATE
    WIFI_SSID=\"$ENV{WIFI_SSID}\"
    WIFI_PASSWORD=\"$ENV{WIFI_PASSWORD}\"
    MQTT_CLIENT=\"$ENV{MQTT_CLIENT}\"
    MQTT_USER=\"$ENV{MQTT_USER}\"
    MQTT_PASSWD=\"$ENV{MQTT_PASSWD}\"
    MQTT_HOST=\"$ENV{MQTT_HOST}\"
    MQTT_PORT=$ENV{MQTT_PORT}
)

# create map/bin/hex file etc.
pico_add_extra_outputs(${NAME})

# enable usb output, disable uart output
pico_enable_stdio_usb(${NAME} 1)
pico_enable_stdio_uart(${NAME} 1)
target_compile_definitions(${NAME} PRIVATE
    PICO_DEFAULT_UART_RX_PIN=17
    PICO_DEFAULT_UART_TX_PIN=16
)

