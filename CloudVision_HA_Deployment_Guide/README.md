# CloudVision HA Deployment (Companion Guide)

The purpose of this folder is to host a series of code snippets for the main article for easier sharing.
The main article can be found on [Arista Community Central](https://arista.my.site.com/AristaCommunity/s/article/cvp-ha-deployment-guide).

## Token generation

```shell
[root@cvp1 ~]# curl -d '{"reenrollDevices":["*"]}' -k https://127.0.0.1:9911/cert/createtoken
{"token":"(cvp1-token)"}
[root@cvp2 ~]# curl -d '{"reenrollDevices":["*"]}' -k https://127.0.0.1:9911/cert/createtoken
{"token":"(cvp2-token)"}
```

## Synchronize the Provisioning Dataset using the backup/restore process

![sync_light.sh](./sync_light.sh)

## Sync script with Secondary cluster check

![sync_v2.sh](./sync_v2.sh)
