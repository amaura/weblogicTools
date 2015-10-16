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

def isGrpInExpr(expr,group):
    return "Grp("+group+")" in expr 

def isAdminLastInExpr(expr):
    exprList=expr.strip('{}').split("|")
    #return len(exprList) == 1 and exprList[0] == "Grp(Administrators)"
    return True


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
                if authorizer.policyExists(resID):
                    curExpr=authorizer.getPolicyExpression(resID)
                    if  isGrpInExpr(curExpr,group):
                        print "Policy already exist for group "+group+" on "+methods['MBean'].split(".")[-1]+"."+target
                    else:
                        authorizer.setPolicyExpression(resID,addGrpToExpr(curExpr,group))
                    
                else:
                        authorizer.createPolicy(resID,initGroupClause)
                print "Result Policy is "+authorizer.getPolicyExpression(resID)+" on "+methods['MBean'].split(".")[-1]+"."+target
            elif action=="revoke":
                if authorizer.policyExists(resID):
                    curExpr=authorizer.getPolicyExpression(resID)
                    if isGrpInExpr(curExpr,group):
                            resExpr=remGrpFromExpr(curExpr,group)
                            if isAdminLastInExpr(resExpr):
                                authorizer.removePolicy(resID)
                            else:
                                authorizer.setPolicyExpression(resID,remGrpFromExpr(curExpr,group))
                                print "Result Policy is "+authorizer.getPolicyExpression(resID)+" on "+methods['MBean'].split(".")[-1]+"."+target
                    else:
	                print "NO policy for "+group+" on "+methods['MBean'].split(".")[-1]+"."+target
		    #print "Access revoked to group "+group+" on "+methods['MBean'].split(".")[-1]+"."+target
                else:
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
 
