# Bulk onboarding devices using token/certificate authentication method

## onboarding_light.py

- Uses the standard packages and no cvprac
- requires the token, the daemon config, device list and credentials to be changed
- can onboard devices either to on-prem or CVaaS
- uses eAPI to configure the EOS switches
- example run: `python onboarding_light.py`

## multi_cluster_onprem.py

- uses eAPI to configure the EOS switches
- requires cvprac: `pip install -r requirements.txt`
- can setup streaming to two on-prem clusters (can be adjusted for more)
- requires service account token from both clusters
- device IPs, CVP IPs and device credentials should be changed
- example run: `python multi_cluster_onprem.py`

## multi_cluster_cvaas_onprem.py

- uses eAPI to configure the EOS switches
- requires cvprac: `pip install -r requirements.txt`
- can setup streaming to an on-prem cluster and a CVaaS tenant (can be adjusted for more)
- requires service account token from both clusters
- device IPs, CVP IP and CVaaS regional URL and device credentials should be changed
- example run: `python multi_cluster_cvaas_onprem.py`

## multi_cluster_cvaas_onprem.yaml

- uses eAPI or SSH to configure the EOS switches
- can setup streaming to an on-prem cluster and a CVaaS tenant (can be adjusted for more)
- requires service account token from both clusters
- device IPs in inventory.yaml, CVP IP and CVaaS regional URL and device credentials should be changed
- example run: `ansible-playbook multi_cluster_cvaas_onprem.yaml -i inventory.yaml`
