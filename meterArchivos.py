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
      #conn = httplib.HTTPConnection("http://www3.witbooking.com:/",8080)
      #headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
      #conn.request("POST","WitBookerAPI-war/webresources/internal/withotel/insert",params,headers)
      #response = conn.getresponse()
      #print response.status, response.reason
      #data = response.read()
      #print "data" , data
      #conn.close()
      #req = urllib2.Request("http://www3.witbooking.com:8080/",params
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

#try:                                                            
#   #s = pxssh.pxssh()
#   #hostname = raw_input('hostname: ')
#   #username = raw_input('username: ')
#   #password = getpass.getpass('password: ')
#   #s.login (hostname, username, password)
#   #s.sendline ('uptime')   # run a command
#   #s.prompt()             # match the prompt
#   #print s.before          # print everything before the prompt.
#   #s.sendline ('ls -l')
#   #s.prompt()
#   #print s.before
#   #s.sendline ('df')
#   #s.prompt()
#   #print s.before
#   #s.login('www.witbooking.com','ftpwitbooking','freeRock!708')
#   #s.sendline('find /httpdocs/v6/multimedia/ -name \'*.png\' -or -name \'*.jpg\' -or -name \'*.gif\'')
#   url = 'www3.witbooking.com'
#   urlFind = url
#   commandFind = 'find /var/www/vhosts/www3.witbooking.com/httpdocs/v6/multimedia/ -name \'*.png\' -or -name \'*.jpg\' -or -name \'*.gif\''
#   s.login(urlFind,'root','WitDevel;')
#   s.sendline(commandFind)
#   s.prompt()
#   content= s.before
#   fil = open('entry.txt','w')
#   fil.write(content)
#   fil.close()
#   #print before 
#   print "Connection closed to ssh remote"
#   errorLog = open('logs/error.log','w')
#   successLog = open('logs/success.log','w')
#   for line in content.splitlines(True)[1:]:
#     #print "line" , line
#     lineRQ =map(lambda x: x.strip(),line.split("/"))
#     msg = '\n'+str(line.strip())+" len: "+str(len(lineRQ))
#     if len(lineRQ) >= 8:
#       lineR = lineRQ[-4:]
#       #print "lineR" , lineR
#       successLog.write(lineR[2])
#       #params = urllib.urlencode({'hotelTicker':lineR[0],'entiy':lineR[1],'idEntity':line[2],'fileNane':lineR[3]})
#       try:
#         params = urllib.urlencode({'hotelTicker':lineR[0],'entiy':lineR[1],'idEntity':int(lineR[2]),'fileName':lineR[3]})
#         print params
#         #conn = httplib.HTTPConnection("http://www3.witbooking.com:/",8080)
#         #headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
#         #conn.request("POST","WitBookerAPI-war/webresources/internal/withotel/insert",params,headers)
#         #response = conn.getresponse()
#         #print response.status, response.reason
#         #data = response.read()
#         #print "data" , data
#         #conn.close()
#         #req = urllib2.Request("http://www3.witbooking.com:8080/",params
#         conn= urllib.urlopen(url+":8080/WitBookerAPI-war/webresources/internal/withotel/insert", params) 
#         htmlGet = html.fromstring(f.read())
#         print(etree.tostring(htmlGet,pretty_print=True))
#         conn.close()
#       except ValueError:
#         print msg
#         errorLog.write(msg)
#     else:
#       print msg
#       errorLog.write(msg)
#   errorLog.close()
#   successLog.close()
#except pxssh.ExceptionPxssh, e:
#    print "pxssh failed on login."
#    print str(e)
