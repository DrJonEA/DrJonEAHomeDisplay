/***
 * Core MQTT Agent Config.
 */

#ifndef CORE_MQTT_AGENT_CONFIG_H_
#define CORE_MQTT_AGENT_CONFIG_H_

#ifndef LIBRARY_LOG_LEVEL
#define LIBRARY_LOG_LEVEL  LOG_INFO
#endif

#ifndef LIBRARY_LOG_NAME
#define LIBRARY_LOG_NAME    "CORE_MQTT_AGENT"
#endif


#include "logging_stack.h"

#define MQTT_AGENT_COMMAND_QUEUE_LENGTH              (50) //( 25 )
#define MQTT_COMMAND_CONTEXTS_POOL_SIZE              ( 10 )


#endif //CORE_MQTT_AGENT_CONFIG_H_
