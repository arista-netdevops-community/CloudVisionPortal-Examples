# Configlet Builder - Self Signed SSL profile 
## Description
This configlet builder script will do the following. 
1. When hitting the Generate button, will create a self-signed certificate and the associated key on the selected device. 
2. When applying the configlet builder to a device, will generate the configuration to create a new SSL profile and apply that profile to the management http-server configuration. 


## How to use
### Configlet Builder creation
1. Go to the Configlet-Builder section in CVP (Provisioning > Configlets > '+' icon >  Configlet builder)
2. Give a name to the new configlet builder (Ex: SelfSignedSSLProfile)
3. Copy-paste the content of `generate_self_signed_certificate.py` inside the Main Script section
4. Modify the `VARIABLES` section to match your environment
5. Save

### Configlet usage
1. Go to the `Network Provisioning` page
2. Right click on the device you would like to apply the configlet-builder > Manage > Configlet
3. Select the Configlet Builder
4. Hit the button `Generate`
5. Hit `Validate`
6. Execute the task to push the new configuration to the switch


### Verification: 
On the switch, the following commands can be used to make sure that the configuration is valid: 
* `dir certificate:`
* `dir sslkey:`
* `show running-config section ssl`
* `show management api http-commands` (Make sure that the `SSL Profile` field is valid)
* `bash openssl x509 -noout -text -in /persist/secure/ssl/certs/self-signed.crt` (to get more details about the generated certificate)
