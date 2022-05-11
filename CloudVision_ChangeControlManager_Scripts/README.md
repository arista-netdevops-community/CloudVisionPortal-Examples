# CVP_CCM

These scripts are to be used in the Change Management Workflow. They use various internal CVP libraries to execute tests on either Arista switches or Linux devices. If the tests are successful the scripts will exit cleanly otherwise they will raise an exception or assert error.

To test the scripts:

`/cvpi/tools/script-util test -path <python file> -config <yaml file>`

To upload the scripts:

`/cvpi/tools/script-util upload -path <python file> -config <yaml file>`

**check_switchType**

Change Control script that uses the arguments provided by check_switchType.yaml to check the switch type (model). The script uses the model description returned by the show version command and compares this to the switchType provided in the script arguments yaml file. The arguments in the yaml file are as follows:
   switchType - required model name that the switch needs to be for the change workflow to progress

The script uses the internal CVP library "Device" to access the eAPI interface on the target Arista EOS switch it then executes the "show version" and "show hostname" commands to gather the required information for the script. The script will fail if the switchType does not match the modelName in the show version return.

**device_ping**

Change Control script that uses the arguments provided by device_ping.yaml to check connectivity between a number of client devices and their targets. The arguments in the yaml file are as follows:
   deviceList - list of Linux clients to ping the target list from
   targetList - list of devices to ping from the Linux clients
   passmark   - percentage of received pings required to Pass each ping test
   failCount  - number of ping tests that can fail before the ping_device script fails
   username   - username to access the Linux clients
   password   - password to use to the client access devices
   pingCount  - number of Pings to send from each client to each target
   timeout    - time to wait for each ping process to complete, this prevents script from hanging if the pings
                  fail or take too long

The script uses paramiko to access each client using SSH and then executes a ping command to each target.

**page_check**

Change Control script that uses the arguments provided by page_check.yaml to check if a web page is reachable from a number of client devices. The arguments in the yaml file are as follows:
   pageURL - the web page to access from the specified clients.
   deviceList - a comma separated list of clients to check the web page from, note this not a yaml list but a
                  comma separated text string.
   failCount  - number of page reachability tests that can fail before the web_check script fails
   username   - username to access the client devices
   password   - password to use to the client access devices
   timeout    - how long to wait for a response from the web page

The script uses paramiko to access each client using SSH and then executes a curl command to reach the web page.

**clean-flash**

Change Control script that removes all EOS images except the boot image from /mnt/flash/.

**AbootPatch**

This script will install the Aboot patch for Field Notice 044

The image can be downloaded from any server using https.  File source is defined in the YAML file argument "extension_URL"

If using CVP as source for the patch file, it requires that CVP has an image bundle containing that Aboot patch file in it

If the installation is done over a none default VRF, change the VRF argument in the YAML config file

you need to define the name of the RPM file in the YAML file argument "extention"

**Image_preload**

This script downloads an EOS image on the selected switch flash.  This is usefull to save time during a maintenance window as the image will already be on the switch ready to be installed instead of copied to each switch during the maintenance window.

Users must edit the YAML file to define the correct repository, vrf and EOS file name

**push_token**

This script is an example on how to push an onboarding token to EOS devices (can be modified to create any file on EOS too).

**Migrate to CVaaS**

This script will migrage the selected node to a CVaaS instance.

An onboarding token needs to be generated on CVaaS and defined in the argument in the YAML file.  Onboarding tokens are generic and can be used for multiple devices.  Please generate one that will be valid for the duration of the onbording.  To update the token in the YAML file, the user-defined action needs to be removed and re-added.

To validate if a token has expired, you can check here: https://jwt.io/

If the node uses the non default VRF, it needs to be defined in the YAML file arguments

The node will start streaming telemetry to the CVaaS instance which will automatically add the node in the inventory.
