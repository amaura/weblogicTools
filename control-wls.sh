#!/bin/bash
#Variables
WLST=/u01/app/oracle/middleware/oracle_common/common/bin/wlst.sh
#Could be useful if SSL conf is changed
#export WLST_PROPERTIES='-Dweblogic.security.SSL.ignoreHostnameVerification=true -Dweblogic.security.CustomTrustKeyStoreType="JKS" -Dweblogic.security.TrustKeyStore=CustomTrust -Dweblogic.security.CustomTrustKeyStoreFileName="/u01/data/domains/keystores/trust.jks"'


message()
{
echo
echo "[$(date '+%Y-%m-%d %H:%M:%S')]" $1
echo
}


usage() {
        echo "Usage : $0 -o start|stop|status [-a][-s ms1,[ms2],... ][-n ms]"
}

message "Starting Weblogic Control script"
#Main
while getopts ":ao:s:n:" opt; do
  case $opt in
    a)
      ALL_SERVERS=Y
      ;;
    o)
      SCRIPT_ACTION=$OPTARG
      ;;
    s)
      SERVER_LIST=${OPTARG//,/ }
      ;;
    n)
      NAME_PREFIX=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      usage
      exit 1
      ;;
  esac
done

if [ "$NAME_PREFIX" = "" ];then
        NAME_PREFIX=server
fi

#Check validity of options
if [[ $SCRIPT_ACTION != "start" &&  "$SCRIPT_ACTION" != "stop" && "$SCRIPT_ACTION" != "status" ]] ;then
usage
exit 1
fi

if [[ "$ALL_SERVERS" == "Y" && "$SERVER_LIST" != "" ]]; then
usage
exit 1
fi

if [[ "$ALL_SERVERS" != "Y" && "$SERVER_LIST" == "" ]]; then
usage
exit 1
fi

#Source the local environment
. /u01/data/domains/*/bin/setDomainEnv.sh 2>&1 >/dev/null


#Getting all local servers
get_local_servers()
{
LOCAL_MACHINE_NUMBER=${HOSTNAME: -1}
RESULT=$(grep "<server>" $DOMAIN_HOME/config/config.xml -A1 |grep -Po "(?<=name>).*_${NAME_PREFIX}_${LOCAL_MACHINE_NUMBER}.*(?=</name)")
if [[ $LOCAL_MACHINE_NUMBER == 1 ]]; then
        RESULT="$(grep "<server>" $DOMAIN_HOME/config/config.xml -A1 |grep -Po "(?<=name>).*adminserver(?=</name)") $RESULT"
fi
echo $RESULT
}

get_all_servers()
{
RESULT=$(grep "<server>" $DOMAIN_HOME/config/config.xml -A1 |grep -Po "(?<=name>).*_${NAME_PREFIX}_.*(?=</name)")
#RESULT="$(grep "<server>" $DOMAIN_HOME/config/config.xml -A1 |grep -Po "(?<=name>).*adminserver(?=</name)") $RESULT"
echo $RESULT
}

get_admin_server()
{
RESULT=$(grep "<server>" $DOMAIN_HOME/config/config.xml -A1 |grep -Po "(?<=name>).*_adminserver(?=</name)")
echo $RESULT
}

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

control_wlst()
{
message "Decrypting Weblogic Password"
CLEAR_PASSWORD=$(decrypt_wls_password)
TEMP_CONTROL=$(mktemp)
cat > $TEMP_CONTROL <<EOF
import sys

if "adminserver" in sys.argv[2] and sys.argv[1] == "start":
    nmConnect ('weblogic','$CLEAR_PASSWORD','$HOSTNAME','5556','${DOMAIN_HOME##*/}','$DOMAIN_HOME','SSL')
    nmStart(sys.argv[2])

connect('weblogic','$CLEAR_PASSWORD','t3://${HOSTNAME%?}1:7001')

print "Action is "+ sys.argv[1]

for i in range(2,len(sys.argv)):
    if sys.argv[1] == "start":
        try:
            if "adminserver" not in sys.argv[i]:
                start(sys.argv[i], 'Server', block='false')
        except WLSTException, e:
            #print "Server "+sys.argv[i]+" is already RUNNING"
            print e
            dumpStack()
    elif sys.argv[1] == "status":
        try:
            #srvstatus = nmServerStatus(sys.argv[i])
            #srvstatus = state(sys.argv[i],'Server')
            #print "Server "+sys.argv[i]+" is "+srvstatus+" "
            state(sys.argv[i])
        except WLSTException, e:
            print "Server "+sys.argv[i]+" is UNKNOWN STATUS"
    else:
        try:
            shutdown(sys.argv[i],'Server','false',120,block='false')
        except WLSTException, e:
            print e
            dumpStack()
            print "Server "+sys.argv[i]+" is probably not running"


EOF
message "Running Weblogic WLST"
$WLST $TEMP_CONTROL $@
rm $TEMP_CONTROL
}

if [[ "$ALL_SERVERS" == "Y" ]]; then
        SERVER_LIST=$(get_all_servers)
        ADMIN_SERVER=$(get_admin_server)
fi

if [[ "$SCRIPT_ACTION" == "start" ]]; then
        control_wlst start $ADMIN_SERVER $SERVER_LIST
fi


if [[ "$SCRIPT_ACTION" == stop ]]; then
        control_wlst stop $SERVER_LIST $ADMIN_SERVER
fi

if [[ "$SCRIPT_ACTION" == "status" ]]; then
        control_wlst status $ADMIN_SERVER $SERVER_LIST
fi

message "End of weblogic control script"
