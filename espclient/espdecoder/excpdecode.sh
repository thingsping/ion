#!/bin/bash

elf="../.pio/build/nodemcuv2/firmware.elf"

java -jar EspStackTraceDecoder.jar ./xtensa-lx106-elf-addr2line $elf exception.dump
