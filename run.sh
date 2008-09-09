#!/bin/bash

cat extensions.conf | ./astograph.py | dot -Tpng:cairo > go.png
