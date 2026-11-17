# wolfMQTT client library with TLS (ENABLE_MQTT_TLS) over wolfSSL, single threaded use.
# Options come from ${WOLFMQTT_PORT_DIR}/wolfmqtt/options.h rather than
# WOLFMQTT_USER_SETTINGS, whose user_settings.h would clash with wolfSSL's.

if (NOT DEFINED WOLFMQTT_DIR)
    set(WOLFMQTT_DIR "${CMAKE_CURRENT_LIST_DIR}/../../lib/wolfmqtt")
endif()
if (NOT DEFINED WOLFMQTT_PORT_DIR)
    set(WOLFMQTT_PORT_DIR "${CMAKE_CURRENT_LIST_DIR}/port/wolfmqtt")
endif()

add_library(wolfmqtt STATIC)

target_sources(wolfmqtt PRIVATE
    ${WOLFMQTT_DIR}/src/mqtt_client.c
    ${WOLFMQTT_DIR}/src/mqtt_packet.c
    ${WOLFMQTT_DIR}/src/mqtt_socket.c
)

target_include_directories(wolfmqtt PUBLIC
    ${WOLFMQTT_PORT_DIR}
    ${WOLFMQTT_DIR}
)

target_link_libraries(wolfmqtt PUBLIC
    pico_stdlib
    wolfssl
)
