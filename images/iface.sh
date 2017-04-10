#!/bin/bash

brctl addbr br1
ifconfig br1 10.99.101.1/24

brctl addbr br2
ifconfig br2 10.99.102.1/24

brctl addbr br3
ifconfig br3 10.99.103.1/24

brctl addbr br4
ifconfig br4 10.99.104.1/24

brctl addbr br5
ifconfig br5 10.99.105.1/24

brctl addbr br6
ifconfig br6 10.99.106.1/24

brctl addbr br7
ifconfig br7 10.99.107.1/24

brctl addbr br8
ifconfig br8 10.99.108.1/24

brctl addbr br9
ifconfig br9 10.99.109.1/24

brctl addbr br10
ifconfig br10 10.99.110.1/24
