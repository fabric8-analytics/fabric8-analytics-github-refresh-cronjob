#!/bin/bash

set -ex

. cico_setup.sh

./runtests.sh

build_image

push_image