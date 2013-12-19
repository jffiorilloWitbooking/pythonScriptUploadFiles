#!/usr/bin/python

from meterArchivos import getFilesAsString,createFolder,serverHash, executeRemote
import pexpect
import sys
import time
import os
import sys

def fetchFileSCP(source,dest,password,child=None):
  expectations = ['[Pp]assword',
           'continue (yes/no)?',
           pexpect.EOF,
           pexpect.TIMEOUT,
           'Name or service not known',
           'Permission denied',
           'No such file or directory',
           'No route to host',
           'Network is unreachable',
           'failure in name resolution',
           'No space left on device'
          ]
#print "Received Args:",child, args
  try:
    if not child:
        commandCopy = "scp "+source+" "+dest
#       print "commandCopy '"+commandCopy+"'"
        child = pexpect.spawn( commandCopy)
    res = child.expect( expectations )
#   print "Child Exit Status :",child.exitstatus
#   print  res,"::",child.before," :After:",child.after
    if res == 0:
      child.sendline(password)
      return fetchFileSCP(source,dest,password,child)
    if res == 1:
      child.sendline('yes')
      return fetchFileSCP(source,dest,password,child)
    if res == 2:
      line = child.before
      print "Line:",line
#     print "Now check the result and return status."
    if res == 3:
      print "TIMEOUT Occurred."
      child.kill(0)
      return False
    if res >= 4:
      child.kill(0)
      print "ERROR:",expectations[res]
      return False
    return True
  except:
    import traceback; traceback.print_exc()
    print "Did file finish?",child.exitstatus



def getFilesAsStringFromServerName(serverName):
  if not serverName in serverHash.keys():
    print serverName, "not configured."
  else:
    server = serverHash[serverName]
#   url = server[0]
    urlFind = server[1]
    remoteDir = server[2]
    userFtp = server[3]
    passFtp = server[4]
    commandLine = "find "+remoteDir+" -name '*.txt'"
    path=createFolder(serverName,"runToDeleteTxt")
#   if path[-1] is not "/":
#     path +="/"
    pathFiles = path+"/files/"
    print "'"+str(path)+"'"
    if not os.path.exists(pathFiles):
      os.makedirs(pathFiles)
    content = getFilesAsString(urlFind,userFtp,passFtp,commandLine,path)
    split = content.split('\r\n')[1:-1]
    for line in split:
      print line
      source = userFtp+"@"+urlFind+":"+line
      if "multimedia" in line.split("/"):
        dest = pathFiles+reduce(lambda x,y: x+"_"+y if x is not "" else y , line.split("/")[line.split("/").index("multimedia")+1:],"")
#       dest = pathFiles+line.split("/")[-1]
        fetchFileSCP(source,dest,passFtp)
#       command = "rm "+line
#       print executeRemote(urlFind,userFtp,passFtp,command)
#       raw_input('Enter any key to continue...')


commandLine = "find /home/jose/Desktop/prueba/ -name '*.txt'"

getFilesAsStringFromServerName("test")

# if __name__ == '__main__':
#stat = True
#stat = fetchFileSCP(None,sys.argv[1])
#if stat:
#    print "File Transferred successfully."
#else:
#    print "Failure while copying files securely."
