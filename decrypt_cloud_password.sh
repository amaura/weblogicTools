#!/bin/bash
#Variables
WLST=/u01/app/oracle/middleware/oracle_common/common/bin/wlst.sh

#Source the local environment
. /u01/data/domains/*/bin/setDomainEnv.sh 2>&1 > /dev/null

decrypt_wls_password()
{
PASSWORD_ENC=$(grep -Po "(?<=<node-manager-password-encrypted>).*(?=</node-manager-password-encrypted>)" $DOMAIN_HOME/config/config.xml)
TEMP_DECRYPT=$(mktemp)
cat > $TEMP_DECRYPT <<EOF
import os
import weblogic.security.internal.SerializedSystemIni
import weblogic.security.internal.encryption.ClearOrEncryptedService

def decrypt(domain, encryptedPassword):
    domainPath = os.path.abspath(domain)
    es = weblogic.security.internal.SerializedSystemIni.getEncryptionService(domainPath)
    ces = weblogic.security.internal.encryption.ClearOrEncryptedService(es)
    password = ces.decrypt(encryptedPassword)

    print "--->"+password

try:
        decrypt(sys.argv[1], sys.argv[2])
except:
    print "Exception: ", sys.exc_info()[0]
    dumpStack()
    raise
EOF

$WLST $TEMP_DECRYPT $DOMAIN_HOME $PASSWORD_ENC 2>&1 | grep -Po "(?<=--->).*"

rm $TEMP_DECRYPT
}

echo $(decrypt_wls_password)
