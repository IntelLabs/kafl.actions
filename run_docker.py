#!/usr/bin/env python3

import os
import argparse
import grp
import subprocess
from pathlib import Path
from pprint import pprint
from contextlib import suppress

KAFL_DOCKER_WORKDIR = '/mnt/workdir'

parser = argparse.ArgumentParser("run_docker.py")
parser.add_argument("--action", choices=['fuzz', 'cov'])
parser.add_argument("--timeout")
parser.add_argument("--workdir")
parser.add_argument("--input")
parser.add_argument("--bios")
parser.add_argument("--kernel")
parser.add_argument("--initrd")
parser.add_argument("--seed_dir")
parser.add_argument("--config_file")
parser.add_argument("--extra_args")

namespace = parser.parse_args()
inputs = vars(namespace)

docker_volumes = []
docker_envs = []
kafl_args = []
# convert empty strings to None values
inputs.update({k:None for k,v in inputs.items() if not v})


# process inputs
docker_volumes.extend([
    '-v', f"{Path(inputs['workdir']).absolute()}:{KAFL_DOCKER_WORKDIR}"
])

if inputs['timeout'] is not None:
    # convert str to int
    inputs['timeout'] = int(inputs['timeout'])
if inputs['input'] is not None:
    docker_volumes.extend([
        '-v', f"{Path(inputs['input']).absolute()}:/mnt/cov_input"
    ])
    kafl_args.extend(['--input', '/mnt/cov_input'])
if inputs['config_file'] is not None:
    docker_volumes.extend([
        '-v', f"{Path(inputs['config_file']).absolute()}:/mnt/custom_settings.yaml"
    ])
    docker_envs.extend(['-e', 'KAFL_CONFIG_FILE=/mnt/custom_settings.yaml'])
if inputs['bios'] is not None:
    docker_volumes.extend([
        '-v', f"{Path(inputs['bios']).absolute()}:/mnt/bios"
    ])
    kafl_args.extend(['--bios', '/mnt/bios'])
if inputs['kernel'] is not None:
    docker_volumes.extend([
        '-v', f"{Path(inputs['kernel']).absolute()}:/mnt/kernel"
    ])
    kafl_args.extend(['--kernel', '/mnt/kernel'])
if inputs['initrd'] is not None:
    docker_volumes.extend([
        '-v', f"{Path(inputs['initrd']).absolute()}:/mnt/initrd"
    ])
    kafl_args.extend(['--initrd', '/mnt/initrd'])
if inputs['extra_args'] is not None:
    kafl_args.extend(inputs['extra_args'].split(' '))

kvm_group = grp.getgrnam('kvm')
cmdline = [
    'docker', 'run', '--rm', '--device=/dev/kvm',
    '--user', f"{os.getuid()}:{os.getgid()}",
    '--group-add', str(kvm_group.gr_gid)
]
cmdline.extend(docker_volumes)
cmdline.extend(docker_envs)
cmdline.extend(['--pull', 'always'])
cmdline.append('intellabs/kafl')
cmdline.append(namespace.action)
cmdline.extend(kafl_args)

pprint(cmdline)

with suppress(subprocess.TimeoutExpired):
    subprocess.check_call(cmdline, timeout=inputs['timeout'])
