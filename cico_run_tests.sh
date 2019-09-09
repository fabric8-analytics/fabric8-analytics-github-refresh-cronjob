#!/bin/bash

set -ex

. cico_setup.sh

./qa/runtests.sh

build_image

push_image
