# set-ethernet-max-ring-buffer

## Intro

Maximizing NIC Ring Buffer is a common task when the host encounters drop packets or loss of data situations on the network. However, the maximum ring buffer values can be different on different NICs.

This small utility will detect the maximum RX/TX ring buffer values and set them to those values on the specified NIC. This could save some time for engineers to investigate and set up commands for tuning ring buffer manually.

In order to make the ring buffer change permanently, please use some facilities that can ensure the command run after OS started.

## Dependencies

This utility does not need any extra command dependencies. It utilized related `ETHTOOL_*` ioctl commands to complete the ring buffer configuration.

## Compilation

```
$ gcc -g -Wall -Wextra -Wpedantic -o set-ethernet-max-ring-buffer set-ethernet-max-ring-buffer.c
```

## Usage

```
$ ./set-ethernet-max-ring-buffer
usage: ./set-ethernet-max-ring-buffer -d <ethernet device name>
```

## Example

```
$ sudo ./set-ethernet-max-ring-buffer -d eno1
Setting RX Ring Buffer from 256 to 4096
Setting TX Ring Buffer from 256 to 4096
$ sudo ethtool -g eno1
Ring parameters for eno1:
Pre-set maximums:
RX:             4096
RX Mini:        n/a
RX Jumbo:       n/a
TX:             4096
Current hardware settings:
RX:             4096
RX Mini:        n/a
RX Jumbo:       n/a
TX:             4096
```

## Reference

[Monitoring and tuning the RX ring buffer](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/configuring_and_managing_networking/monitoring-and-tuning-the-rx-ring-buffer_configuring-and-managing-networking)

[Queueing in the Linux Network Stack](https://www.linuxjournal.com/content/queueing-linux-network-stack)
