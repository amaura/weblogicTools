clause='{Grp(JMSMonitor)}'
ROmethods=['getCursorEndPosition','getCursorSize','getCursorStartPosition','getItems','getMessage','getMessages','getNext','getPrevious','sort']
connect(username='weblogic',url='t3://gate0141:10001',password='welcome1')
domainName=cmo.getName()
print domainName
cd('SecurityConfiguration/'+domainName+'/DefaultRealm/myrealm/Authorizers/XACMLAuthorizer')


for ROm in ROmethods :
    policy='type=<jmx>, operation=invoke, application=, mbeanType=weblogic.management.runtime.JMSDestinationRuntimeMBean, target='+ROm
    #cmo.removePolicy(policy)
    cmo.createPolicy(policy,clause)
