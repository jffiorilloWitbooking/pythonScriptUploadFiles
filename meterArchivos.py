import pxssh
import getpass
import httplib,urllib,urllib2
from lxml import etree, html

def getValues():
  hostname = raw_input('hostname: ')
  username = raw_input('username: ')
  password = getpass.getpass('password: ')
  return [hostname,username,password]

def getFilesAsString(urlFind,commandFind):
  try:                                                            
    s = pxssh.pxssh()
    s.login(urlFind,'root','WitDevel;')
    s.sendline(commandFind)
    s.prompt()
    content= s.before
    fil = open('entry.txt','w')
    fil.write(content)
    fil.close()
    #print before 
    s.logout()
    return content
  except pxssh.ExceptionPxssh, e:
      print "pxssh failed on login."
      print str(e)

def sendFile(url,lineR,successLog,errorLog,msg):
  #print "lineR" , lineR
  successLog.write(lineR[2])
  #params = urllib.urlencode({'hotelTicker':lineR[0],'entiy':lineR[1],'idEntity':line[2],'fileNane':lineR[3]})
  try:
    hotelTicker = lineR[0]
    entity = lineR[1]
    idEntity = int(lineR[2])
    fileName = lineR[3]
    if hotelTicker == 'hoteldemo.com.v6':
      print lineR
      params = urllib.urlencode({'hotelTicker':hotelTicker,'entity':entity,'idEntity':idEntity,'fileName':fileName})
      print params
      conn= urllib.urlopen(url+":8080/WitBookerAPI-war/webresources/internal/withotel/insert", params) 
      htmlGet = html.fromstring(conn.read())
      print(etree.tostring(htmlGet,pretty_print=True))
      conn.close()
  except ValueError:
    print msg
    errorLog.write(msg)


def main():
  #url = "http://localhost"
  url = "http://www3.witbooking.com"
  urlFind = "www3.witbooking.com"
  commandFind = 'find /var/www/vhosts/www3.witbooking.com/httpdocs/v6/multimedia/ -name \'*.png\' -or -name \'*.jpg\' -or -name \'*.gif\''
  content = getFilesAsString(urlFind,commandFind)
  errorLog = open('logs/error.log','w')
  successLog = open('logs/success.log','w')
  i = 0
  totalString = content.splitlines(True)[1:]
  for line in totalString:
    lineRQ =map(lambda x: x.strip(),line.split("/"))
    msg = '\n'+str(line.strip())+" len: "+str(len(lineRQ))
    if len(lineRQ) >= 8:
      lineR = lineRQ[-4:]
      i+=1
      #print 'llamar con ',lineR
      sendFile(url,lineR,successLog,errorLog,msg)
    else:
      print msg
      errorLog.write(msg)
  print "i : " , i, "total: " , len(totalString)
  errorLog.close()
  successLog.close()

main()
