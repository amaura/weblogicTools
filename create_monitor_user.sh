#!/bin/bash
#Variables
WLST=/u01/app/oracle/middleware/oracle_common/common/bin/wlst.sh

if [ $# -ne 2 ]; then
echo "Usage : $0 <monitor user> <monitor password>"
exit 1
fi

MONITOR_USER=$1
MONITOR_PASSWORD=$2

message()
{
echo
echo "[$(date '+%Y-%m-%d %H:%M:%S')]" $1
echo
}




#Source the local environment
. /u01/data/domains/*/bin/setDomainEnv.sh 2>&1 /dev/null



decrypt_wls_password()
{
PASSWORD_ENC=$(grep -Po "(?<=<node-manager-password-encrypted>).*(?=</node-manager-password-encrypted>)" $DOMAIN_HOME/config/config.xml)
TEMP_DECRYPT=$(mktemp)
cat > $TEMP_DECRYPT <<EOF
import os
import weblogic.security.internal.SerializedSystemIni
import weblogic.security.internal.encryption.ClearOrEncryptedService

def decrypt(agileDomain, encryptedPassword):
    agileDomainPath = os.path.abspath(agileDomain)
    encryptSrv = weblogic.security.internal.SerializedSystemIni.getEncryptionService(agileDomainPath)
    ces = weblogic.security.internal.encryption.ClearOrEncryptedService(encryptSrv)
    password = ces.decrypt(encryptedPassword)

    print "--->"+password

try:
        decrypt(sys.argv[1], sys.argv[2])
except:
    print "Exception: ", sys.exc_info()[0]
    dumpStack()
    raise
EOF

java weblogic.WLST $TEMP_DECRYPT $DOMAIN_HOME $PASSWORD_ENC 2>&1 | grep -Po "(?<=--->).*"

rm $TEMP_DECRYPT
}

create_monitor_user()
{
message "Decrypting Weblogic Password"
CLEAR_PASSWORD=$(decrypt_wls_password)

TEMP_WLST_SCRIPT=$(mktemp)
cat > $TEMP_WLST_SCRIPT <<EOF
connect('weblogic','$CLEAR_PASSWORD','t3://${HOSTNAME%?}1:7001')
domainName=get('Name')
da='/SecurityConfiguration/'+domainName+'/Realms/myrealm/AuthenticationProviders/DefaultAuthenticator'
cd(da)
if cmo.userExists('$MONITOR_USER'):
    print "User $MONITOR_USER already exists"
    cmo.resetUserPassword('$MONITOR_USER','$MONITOR_PASSWORD')
    print "Password changed"
    cmo.addMemberToGroup('Monitors','$MONITOR_USER')
else:
    print "User $MONITOR_USER does not exist"
    cmo.createUser('$MONITOR_USER','$MONITOR_PASSWORD','Prometheus User')
    cmo.addMemberToGroup('Monitors','$MONITOR_USER')
    print "User $MONITOR_USER created and added to Monitors group"
EOF
message "Running Weblogic WLST"
$WLST $TEMP_WLST_SCRIPT
rm $TEMP_WLST_SCRIPT
}
message "start of create monitor User script"

#Main
create_monitor_user

message "End of Create Monitor User script"
