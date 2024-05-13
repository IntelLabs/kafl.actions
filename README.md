# DISCONTINUATION OF PROJECT #  
This project will no longer be maintained by Intel.  
Intel has ceased development and contributions including, but not limited to, maintenance, bug fixes, new releases, or updates, to this project.  
Intel no longer accepts patches to this project.  
 If you have an ongoing need to use this project, are interested in independently developing it, or would like to maintain patches for the open source software community, please create your own fork of this project.  
  
# kafl.actions

> Run kAFL fuzzer on Github Actions

- [kafl.actions](#kaflactions)
  - [Requirements](#requirements)
  - [Inputs](#inputs)
  - [Examples](#examples)
    - [Fuzzing the Linux kernel](#fuzzing-the-linux-kernel)
      - [Fuzzing](#fuzzing)
      - [Coverage](#coverage)


## Requirements

- Self-hosted Github Actions runner
- kAFL kernel

## Inputs

| Name          | Required | Description                                                                                                                                                                           |
| ------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `action`      | Yes       | kAFL subcommand to execute. Default: `fuzz`                                                                                                                                           |
| `wokrdir`     | No       | kAFL `--workdir` parameter                                                                                                                                                            |
| `input`       | No       | kAFL coverage `--input` parameter                                                                                                                                                     |
| `timeout`     | No       | Execution timeout (useful with `fuzz` subcommand). Default: no timeout                                                                                                                |
| `bios`        | No       | kAFL `--bios` parameter                                                                                                                                                               |
| `kernel`      | No       | kAFL `--kernel` parameter                                                                                                                                                             |
| `initrd`      | No       | kAFL `--initrd` parameter                                                                                                                                                             |
| `seed_dir`    | No       | kAFL `--seed_dir` parameter                                                                                                                                                           |
| `config_file` | No       | Additional configuration file for kAFL ([`KAFL_CONFIG_FILE`](https://github.com/IntelLabs/kafl.fuzzer/blob/master/docs/fuzzer_configuration.md#configuration-sources-and-precedence)) |
| `extra_args`  | No       | Extra kAFL command line arguments                                                                                                                                                                                      |

## Examples

### Fuzzing the Linux kernel

This example demonstrate how to port the [Fuzzing the Linux Kernel](https://intellabs.github.io/kAFL/tutorials/fuzzing_linux_kernel.html) kAFL tutorial in Github Actions.

You can review the corresponding [kernel.yml](https://IntelLabs/kafl.actions/tree/master/.github/workflows/kernel.yml) workflow.

#### Fuzzing

~~~yaml
      - name: Create workdir
        run: mkdir kafl_workdir

      - name: Fuzz Linux kernel
        uses: IntelLabs/kafl.actions@master
        with:
          action: fuzz
          workdir: kafl_workdir
          timeout: 600 # run for 10 minutes
          kernel: targets/linux-kernel/linux-guest/arch/x86/boot/bzImage
          # additional config file to specify extra QEMU boot parameters and toggle devices required for virtio
          config_file: targets/linux-kernel/kafl_config.yaml
          extra_args: >-
            --redqueen --grimoire --afl-dumb-mode --radamsa
            --trace
            -t 0.1 -ts 0.01
            -m 512
            --log
            --log-hprintf
            -p 2
~~~

#### Coverage

Assuming we ran our fuzzing session with `--log-hprintf`, we can get the IP ranges in `$KAFL_WORKDIR/hprintf_00.log`,
and store them in the `GITHUB_ENV` as `kafl_ipx` variables.

~~~yaml
      - name: Get IP ranges from hprintf_00 log file
        run: |
          echo kafl_ip0=$(grep -oP 'Setting range 0:\s+\K.*-.*' kafl_workdir/hprintf_00.log) >> $GITHUB_ENV
          echo kafl_ip1=$(grep -oP 'Setting range 1:\s+\K.*-.*' kafl_workdir/hprintf_00.log) >> $GITHUB_ENV
~~~

Finally, we can get the coverage

~~~yaml
      - name: Gather coverage info
        uses: IntelLabs/kafl.actions@master
        with:
          action: cov
          # we need to explicitly specify our workdir, since it needs to be mounted as a volume in the Docker container.
          workdir: kafl_workdir
          input: kafl_workdir
          kernel: targets/linux-kernel/linux-guest/arch/x86/boot/bzImage
          config_file: targets/linux-kernel/kafl_config.yaml
          extra_args: >-
            --resume
            -ip0 ${{ env.kafl_ip0 }}
            -ip1 ${{ env.kafl_ip1 }}
            -m 512
            -t 2
            -p 12
~~~
