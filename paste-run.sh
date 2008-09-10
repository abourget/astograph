#!/bin/bash

echo "Just paste some extensions.conf configuration in here, and hit Ctrl+D"

cat | ./astograph.py | dot -Tpng:cairo > graph.png
