#!/usr/bin/env python3

import argparse
import os
import re
import subprocess
import sys


def test_device_type(device):
    """
    test if input device is Ethernet type
    """
    type_file = f"/sys/class/net/{device}/type"

    if not os.path.exists(type_file):
        return False
    else:
        try:
            with open(type_file, "rt") as f:
                type_flag = f.readlines()[0].strip()
        except:
            return False
        else:
            if type_flag == "1":
                return True
            else:
                return False


def get_ring_buffer(device):
    """
    get rx/tx ring buffer values from input device
    """
    # ring_buffer: [rx_max_value, tx_max_value, rx_current_value, tx_current_value]
    ring_buffer = []

    try:
        output = subprocess.run(["ethtool", "-g", device], capture_output=True)
    except:
        return ring_buffer
    else:
        if output.returncode != 0:
            return ring_buffer
        else:
            for line in output.stdout.decode().split("\n"):
                if line.startswith("RX:"):
                    rx_match = re.match(r"RX:\s+(\d+)", line)
                    if rx_match is not None:
                        if rx_match.groups():
                            ring_buffer.append(rx_match.groups()[0])
                        else:
                            ring_buffer.append(None)
                    else:
                        ring_buffer.append(None)
                if line.startswith("TX:"):
                    tx_match = re.match(r"TX:\s+(\d+)", line)
                    if tx_match is not None:
                        if tx_match.groups():
                            ring_buffer.append(tx_match.groups()[0])
                        else:
                            ring_buffer.append(None)
                    else:
                        ring_buffer.append(None)

    return dict(
        zip(
            ["rx_max_value", "tx_max_value", "rx_current_value", "tx_current_value"],
            ring_buffer,
        )
    )


def set_ring_buffer(device, ring_buffer):
    """
    set rx/tx ring buffer to input device
    """
    exit_code = 0

    # return 10 immediately if ethtool does not contain proper ring buffer values
    if not ring_buffer:
        print("ERROR: Could not retrieve Ring Buffer values", file=sys.stderr)
        return 10

    if ring_buffer["rx_max_value"] is None:
        print("RX Maximum Ring Buffer is invalid, skipped.")
    else:
        print(
            f"Setting RX Ring Buffer from {ring_buffer['rx_current_value']} to {ring_buffer['rx_max_value']}"
        )

        try:
            set_rx_ring_buffer_output = subprocess.run(
                ["ethtool", "-G", device, "rx", ring_buffer["rx_max_value"]],
                capture_output=True,
            )
        except Exception as e:
            print(f"ERROR: Failed to set up RX ring buffer: {str(e)}", file=sys.stderr)
            exit_code += 1
        else:
            if set_rx_ring_buffer_output.returncode != 0:
                print(
                    f"ERROR: ethtool returns non-0 exit code while setting up RX ring buffer: {set_rx_ring_buffer_output.stderr.decode().strip()}",
                    file=sys.stderr,
                )
                exit_code += 1

    if ring_buffer["tx_max_value"] is None:
        print("TX Maximum Ring Buffer is invalid, skipped.")
    else:
        print(
            f"Setting TX Ring Buffer from {ring_buffer['tx_current_value']} to {ring_buffer['tx_max_value']}"
        )

        try:
            set_tx_ring_buffer_output = subprocess.run(
                ["ethtool", "-G", device, "tx", ring_buffer["tx_max_value"]],
                capture_output=True,
            )
        except Exception as e:
            print(f"ERROR: Failed to set up TX ring buffer: {str(e)}", file=sys.stderr)
            exit_code += 1
        else:
            if set_tx_ring_buffer_output.returncode != 0:
                print(
                    f"ERROR: ethtool returns non-0 exit code while setting up TX ring buffer: {set_tx_ring_buffer_output.stderr.decode().strip()}",
                    file=sys.stderr,
                )
                exit_code += 1

    return exit_code


if __name__ == "__main__":
    # set up args
    parser = argparse.ArgumentParser(
        description="Set max TX/RX ring buffer for ethernet device"
    )
    parser.add_argument(
        "--device", type=str, required=True, help="Ethernet device name"
    )
    args = parser.parse_args()

    # exit if device is not Ethernet type
    if not test_device_type(args.device):
        print(f"ERROR: {args.device} is not an Ethernet type device", file=sys.stderr)
        sys.exit(5)

    # ethtool needs superuser permission to run. check EUID and exit if it's not root user
    euid = os.geteuid()
    if euid != 0:
        print("Please run this utility under root user permission", file=sys.stderr)
        sys.exit(20)

    # retrieve ring buffer parameters from device
    device_ring_buffer = get_ring_buffer(args.device)

    # set up device ring buffer to max values
    set_ring_buffer_exit_code = set_ring_buffer(args.device, device_ring_buffer)
    sys.exit(set_ring_buffer_exit_code)
