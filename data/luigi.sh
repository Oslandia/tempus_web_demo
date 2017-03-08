#!/bin/bash

here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=$here

workers=2

luigi --local-scheduler --workers $workers --parallel-scheduling --module tasks ExtractAllLayers
sleep 10
luigi --local-scheduler --workers $workers --parallel-scheduling --module tasks WrapperShapeTask --source rdata
luigi --local-scheduler --workers $workers --parallel-scheduling --module tasks WrapperShapeTask --source grandlyon
