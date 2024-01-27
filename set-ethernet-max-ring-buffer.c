#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <linux/ethtool.h>
#include <linux/if.h>
#include <linux/netlink.h>
#include <sys/ioctl.h>
#include <sys/socket.h>

#ifndef SIOCETHTOOL
#define SIOCETHTOOL     0x8946
#endif

struct cmd_context {
    const char *devname;    /* net device name */
    int fd;         /* socket suitable for ethtool ioctl */
    struct ifreq ifr;   /* ifreq suitable for ethtool ioctl */
};

int send_ioctl(struct cmd_context *ctx, void *cmd)
{
    ctx->ifr.ifr_data = cmd;
    return ioctl(ctx->fd, SIOCETHTOOL, &ctx->ifr);
}

static int set_max_ring(struct cmd_context *ctx)
{
    struct ethtool_ringparam ering;
    int err;

    ering.cmd = ETHTOOL_GRINGPARAM;
    err = send_ioctl(ctx, &ering);
    if (err != 0) {
        perror("Cannot get device ring settings");
        return 76;
    }

    /* set up maximum ring buffer values on rx/tx */
    fprintf(stdout, "Setting RX Ring Buffer from %u to %u\n", ering.rx_pending, ering.rx_max_pending);
    if (ering.rx_pending < ering.rx_max_pending) {
        ering.rx_pending = ering.rx_max_pending;
    }

    fprintf(stdout, "Setting TX Ring Buffer from %u to %u\n", ering.tx_pending, ering.tx_max_pending);
    if (ering.tx_pending < ering.tx_max_pending) {
        ering.tx_pending = ering.tx_max_pending;
    }

    ering.cmd = ETHTOOL_SRINGPARAM;
    err = send_ioctl(ctx, &ering);
    if (err != 0) {
        perror("Cannot set device ring parameters");
        return 81;
    }

    return 0;
}

static int ioctl_init(struct cmd_context *ctx)
{
    if (strlen(ctx->devname) >= IFNAMSIZ) {
        fprintf(stderr, "Device name longer than %u characters\n",
            IFNAMSIZ - 1);
        exit(EXIT_FAILURE);
    }

    /* Setup our control structures. */
    memset(&ctx->ifr, 0, sizeof(ctx->ifr));
    strcpy(ctx->ifr.ifr_name, ctx->devname);

    /* Open control socket. */
    ctx->fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (ctx->fd < 0)
        ctx->fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC);
    if (ctx->fd < 0) {
        perror("Cannot get control socket");
        return 70;
    }

    return 0;
}

static void usage(char *prog_name)
{
    fprintf(stderr, "usage: %s -d <ethernet device name>\n", prog_name);
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[])
{
    if (argc != 3) {
        usage(argv[0]);
    }

    int ret_set = 0;
    int ret = 0;
    struct cmd_context ctx = {0};

    int r;
    char *devname;
    opterr = 0;

    while ((r = getopt(argc, argv, "d:")) != -1) {
        switch (r) {
            case 'd':
                devname = optarg;
                break;
            case '?':
                usage(argv[0]);
                break;
            default:
                usage(argv[0]);
                break;
        }
    }

    ctx.devname = devname;
    ret = ioctl_init(&ctx);
    if (ret) {
        return ret;
    }

    ret_set = set_max_ring(&ctx);

    close(ctx.fd);

    return ret_set;
}
