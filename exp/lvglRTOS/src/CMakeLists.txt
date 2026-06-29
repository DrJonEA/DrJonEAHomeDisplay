add_executable(${NAME}
        main.cpp
        Widgets.cpp
        ClockDisplay.cpp
        )

# Pull in our pico_stdlib which pulls in commonly used features
target_link_libraries(${NAME} 
    pico_stdlib
	hardware_pio 
	hardware_adc 
	hardware_dma 
	pico_graphics 
	cosmic_unicorn
	lvgl
	FreeRTOS-Kernel-Heap4 # FreeRTOS kernel and dynamic heap
	freertos_config #FREERTOS_PORT
	pico_cyw43_arch_lwip_sys_freertos
	LWIP_PORT
)

# enable usb output, disable uart output
pico_enable_stdio_usb(${NAME} 1)
pico_enable_stdio_uart(${NAME} 0)


# create map/bin/hex file etc.
pico_add_extra_outputs(${NAME})