# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# Functions

def usage():
    print "Usage : "+sys.argv[0]+" <url> <SOA Role : SOAAdmin|SOAMonitor|SOAOperator> <Group>"
    sys.exit(1)

##### Main #####
if len(sys.argv)-1 != 3:
    usage()

user="weblogic"
url=sys.argv[1]
SOARole=sys.argv[2]
group=sys.argv[3]

password="weblogiC1!"
#password= "".join(java.lang.System.console().readPassword("%s", ["Weblogic Password : "]))

connect(username=user,url=url,password=password)

print "----------------"
print "AVANT CHANGEMENT"
print "----------------"
listAppRoleMembers(appStripe="soa-infra", appRoleName=SOARole)
#grantAppRole(appStripe="soa-infra", appRoleName=SOARole,principalClass="weblogic.security.principal.WLSGroupImpl", principalName=group,forceValidate="false")

print "----------------"
print "APRES CHANGEMENT"
print "----------------"
listAppRoleMembers(appStripe="soa-infra", appRoleName=SOARole)
