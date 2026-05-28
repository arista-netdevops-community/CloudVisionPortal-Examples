# EST Enrollment using studio
 EST protocol allowing simple Enrollment and re-Enrollment of certication without manual intervention for renewals.
 The protocol is using client/server model, for example, Arista switch act as EST client and AGNI as EST server.
 This example studio and action package can be used in CVP/Cvaas to generate the necessary EOS configuration for EST protocol.
 
# Prerequisite for using the EST Studio:
 1. Download Root CAs certificate from AGNI to a local directory. 
    EST and Radsec using different certificates.
 2. intstall into cvaas the latest package certificate_management_x.y.z.tar
 3. Use the certificate_management package to create a self signed certificate for each switch.
 4. Use the certificate_management package to push both EST & Radsec CA certificate into each switch.

# How to use EST studio:
1. Add device into the device selection inside the EST studio.
2. Fill the needed information to generatae the auto-certficaite using EST protocol.
3. Optionally: Fill the Radsec information to generate general dot1x/radsec config using the auto generated certificate. 
   Note: Radsec configuration can also be generated using the built-in "Authentication" studio.
   If you are using the built-in studio, please skill stage 3.
 
# Questions: shaip@arista.com