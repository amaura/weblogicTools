import sys

def usage():
    print "Usage : "+sys.argv[0]+" <username> <password> <url> <module/UDQ>"
    print "Exemple : "+sys.argv[0]+" weblogic password t3s://localhost:7001 SystemModule-1/UDQueue0"
    sys.exit(1)

def askUser():
    choice = raw_input()
    if choice == 'O' or choice == 'o':
        return
    else:
       print "Sortie ..."
       cancelEdit('y')
       sys.exit(0)

if len(sys.argv) < 5:
    usage()

mq=sys.argv[4].split('/')
redirect('/dev/null', 'false')
connect(sys.argv[1],sys.argv[2],sys.argv[3]);
qloc='JMSSystemResources/'+mq[0]+'/JMSResource/'+mq[0]+'/UniformDistributedQueues/'+mq[1]+'/MessageLoggingParams/'+mq[1]
edit()
try:
    startEdit(exclusive='true')
except WLSTException:
    print "Impossible de verrouiller la session d'edition de configuration"
    sys.exit(1)
try:
   cd(qloc)
except WLSTException:
   print "Vous avez spécifié le module : "+mq[0]
   print "Vous avez spécifié la UDQ : "+mq[1]
   print "Impossible de trouver la file"
   cancelEdit('y')
   sys.exit(1)

if cmo.isMessageLoggingEnabled():
    print "Le logging sur la file "+mq[1]+" est activé."
    print "Voulez vous le désactiver ? O/N"
    askUser()
    cmo.setMessageLoggingEnabled(false)
    save()
else:
    print "Le logging sur la file "+mq[1]+" est desactivé."
    print "Voulez vous l'activer ? O/N"
    askUser()
    cmo.setMessageLoggingEnabled(true)
    cmo.setMessageLoggingFormat('%header%,%properties%,%body%')
    save()
activate()
disconnect();
exit()
