# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# Functions
#from weblogic.management.security.authentication import UserReaderMBean


def usage():
    print "Usage : "+sys.argv[0]+" <url> <grant/revoke> <Group> <RW/R>"
    sys.exit(1)


def addGrpToExpr(expr,group):
    exprList=expr.strip('{}').split("|")
    exprList.append("Grp("+group+")")
    return "{"+"|".join(exprList)+"}"

def remGrpFromExpr(expr,group):
    exprList=expr.strip('{}').split("|")
    exprList.remove("Grp("+group+")")
    return "{"+"|".join(exprList)+"}"




def managePolicy(methods,permissions,authorizer,group,action):
    initGroupClause='{Grp('+group+')|Grp(Administrators)}'
    resourceClause='type=<jmx>, operation=invoke, application=, mbeanType='+methods['MBean']+', target='
    if permissions=="R":
        targets=(methods.get('RMethods') or [])
    elif permissions=="RW":
        targets = (methods.get('RMethods') or []) + (methods.get('WMethods') or [])
    else:
        raise ValueError('Unknown Permissions !')
    if targets:
        for target in targets :
            resID=resourceClause+target
            if action=="grant":
                try:
                    if authorizer.policyExists(resID):
                        curExpr=authorizer.getPolicyExpression(resID)
                        authorizer.createPolicy(resID,addGrpToExpr())
                        print "Access granted to group "+group+" on "+methods['MBean'].split(".")[-1]+"."+target
                except weblogic.management.utils.AlreadyExistsException:
                    print "Policy "+authorizer.getPolicyExpression(resID)+" exists on "+methods['MBean'].split(".")[-1]+"."+target
                except weblogic.management.utils.NotFoundException:
                    print "NO policy on "+methods['MBean'].split(".")[-1]+"."+target
            elif action=="revoke":
                try:
                    authorizer.removePolicy(resID)
                    print "Access revoked to group "+group+" on "+methods['MBean'].split(".")[-1]+"."+target
                except weblogic.management.utils.NotFoundException:
                    print "NO policy on "+methods['MBean'].split(".")[-1]+"."+target
            else:
                raise ValueError('Unknown action !')




##### Main #####
if len(sys.argv)-1 != 4:
    usage()

user="weblogic"
url=sys.argv[1]
action=sys.argv[2]
group=sys.argv[3]
permissions=sys.argv[4]


JMSDestMbeanMethods={
'MBean':"weblogic.management.runtime.JMSDestinationRuntimeMBean",
'RMethods':['getCursorEndPosition','getCursorSize','getCursorStartPosition','getItems','getMessage','getMessages','getNext','getPrevious','sort'],
'WMethods':['closeCursor','createDurableSubscriber','deleteMessages','destroyJMSDurableSubscriberRuntime','importMessages','moveMessages','mydelete','pause','pauseConsumption','pauseInsertion','pauseProduction','preDeregister','resume','resumeConsumption','resumeInsertion','resumeProduction']
}

bridgeMBeanMethods={
'MBean':"MessagingBridgeRuntimeMBean",
'WMethods':['start','stop']
}



#password= "".join(java.lang.System.console().readPassword("%s", ["Weblogic Password : "]))
password="welcome1"
connect(username=user,url=url,password=password)

securityRealm=cmo.getSecurityConfiguration().getDefaultRealm()
atzr=securityRealm.lookupAuthorizer('XACMLAuthorizer')

managePolicy(JMSDestMbeanMethods,permissions,atzr,group,action)
managePolicy(bridgeMBeanMethods,permissions,atzr,group,action)
#    getExistingPolicyGroups(atzr)
