#!/bin/bash
while true; do nc.traditional -k -l -p $1 -e ./CHALLENGE; done
