from cvplibrary import CVPGlobalVariables, GlobalVariableNames, Device

#VARIABLES
certname = 'self-signed.crt'
keyname = 'self-signed.key'
duration = '365' # In days
country = 'US'
state = 'CA'
locality = 'SantaClara'
org = 'Example'
ou = 'IT'
key_length = 2048
SSL_profile_name = 'selfSignedSSLProfile'

# Get Device Object
device_ip = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_IP)
device_mac = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_MAC)
device = Device(device_ip)


# Get FQDN of the switch
cmdList = [ "enable" , "show hostname" ]
response_dict = device.runCmds(cmdList)
fqdn = response_dict[1]['response']['fqdn']
# print fqdn


# Generate self-signed certificate and key on the switch
response = device.runCmds([ 'enable', 'security pki key generate rsa 2048 '+keyname,
'security pki certificate generate self-signed '+certname+' key '+keyname+' validity '+duration+
' parameters'+
' common-name ' + fqdn +
' country ' + country +
' state ' + state +
' locality ' + locality +
' organization ' + org +
' organization-unit ' + ou +
' subject-alternative-name dns ' + fqdn + 
' subject-alternative-name ip ' + device_ip])



# Generate EOS configuration on the switch
sslProfileCfg = "management security\n" 
sslProfileCfg += "ssl profile {}\n".format(SSL_profile_name)
sslProfileCfg += "certificate {} key {}\n".format(certname, keyname)
sslProfileCfg += "management api http-commands\n"
sslProfileCfg += "protocol https ssl profile {}\n".format(SSL_profile_name)
print(sslProfileCfg)