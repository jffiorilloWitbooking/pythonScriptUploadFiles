#!/usr/bin/python

import pxssh
import getpass
import httplib,urllib,urllib2
import sys
import getopt
import glob,os 
from lxml import etree, html

def getFilesAsString(urlFind,userFtp,passFtp,commandFind):
  try:                                                            
    s = pxssh.pxssh()
    s.login(urlFind,userFtp,passFtp)
    s.sendline(commandFind)
    s.prompt()
    content= s.before
    fil = open('entry.txt','w')
    fil.write(content)
    fil.close()
    s.logout()
    return content
  except pxssh.ExceptionPxssh, e:
      print "pxssh failed on login."
      print str(e)

def sendFile(url,line,lineR,successLog,errorLog,msg,wait,hotelTickerFail,rep,new,unknow):
  try:
    hotelTicker = lineR[0]
    entity = lineR[1]
    idEntity = int(lineR[2])
    fileName = lineR[3]
    #if hotelTicker == 'hoteldemo.com.v6':
    print lineR
    params = urllib.urlencode({'hotelTicker':hotelTicker,'entity':entity,'idEntity':idEntity,'fileName':fileName})
    print params
    conn= urllib.urlopen(url+":8080/WitBookerAPI-war/webresources/internal/withotel/insert", params) 
    htmlGet = html.fromstring(conn.read())
    msgBonito=etree.tostring(htmlGet,pretty_print=True)
    successLog.write(str(lineR))
    successLog.write(str(params))
    successLog.write(msgBonito)
    print(msgBonito)
    if "The database could not be accessed" in msgBonito or "DataBase '"+hotelTicker+"' Not found." in msgBonito:
      print "hotelTicker "+ hotelTicker + " appended to hotelTickerFail list "
      hotelTickerFail.append(hotelTicker)
    elif "hotelMedia ya existe" in msgBonito:
      rep+=1
    elif "HotelMedia{" in msgBonito:
      new+=1
    else:
      unknow+=1
    conn.close()
  except ValueError:
    print msg
    if (wait):
      raw_input('Error happens, enter any key to continue...')
    errorLog.write(msg)
  return [rep,new,unknow]

def error():
  print 'Arguments required. \nPlease run python meterArchivos.py -h for more information.'
  #print 'test.py -i <inputfile> -o <outputfile>'
  sys.exit(2)

def execute(url,urlFind,commandFind,userFtp,passFtp,wait):
#def main(argv):
  print "ssh "+userFtp+"@"+urlFind
  content = getFilesAsString(urlFind,userFtp,passFtp,commandFind)
  errorLog = open('logs/error.log','w')
  successLog = open('logs/success.log','w')
  i = 0
  totalString = content.splitlines(True)[1:]
  hashMap = {}
  hotelTickerFail = []
  rep=0
  new=0
  unknow=0
  for line in totalString:
    lineRQ =map(lambda x: x.strip(),line.split("/"))
    msg = '\n'+str(line.strip())+" len: "+str(len(lineRQ))
    if len(lineRQ) >= 8:
      lineR = lineRQ[-4:]
      hotelTicker = lineR[0]
      if hashMap.has_key(hotelTicker):
        hashMap[hotelTicker] = hashMap[hotelTicker] + 1
      else:
        hashMap[hotelTicker] = 1
      i+=1
      if not hotelTicker in hotelTickerFail:
        rep,new,unknow = sendFile(url,line,lineR,successLog,errorLog,msg,wait,hotelTickerFail,rep,new,unknow)
    else:
      print msg
      errorLog.write(msg)
  print "i : " , i, "total: " , len(totalString)
  print "rep " , rep , " new ", new , " unknow " , unknow
  print "hotelTickerFail " , hotelTickerFail
  print hashMap
  errorLog.close()
  successLog.close()


def main(argv):
  serverHash = {"luke": [
                  "http://luke.local",
                  "luke.local",
                  "/var/www/vhosts/jpala.luke.local/httpdocs/v6/multimedia",
                  "oper",
                  "wIT_oper13"
                ] ,
            "test" : [
                  "http://www3.witbooking.com",
                  "www3.witbooking.com",
                  "/var/www/vhosts/www3.witbooking.com/httpdocs/v6/multimedia/",
                  "root",
                  "WitDevel;"
                ],
            "prod" : [
                  "http://www.witbooking.com",
                  "www.witbooking.com",
                  "/var/www/vhosts/www.witbooking.com/httpdocs/v6/multimedia",
                  "ftpwitbooking",
                  "freeRock!708"
                ],
            #, "local" : "localhost"
            }
  server = []
  wait = False
  try:
    opts, args = getopt.getopt(argv,"hs:rw",["server="])
    #opts, args = getopt.getopt(argv,"hs:o:",["ifile=","ofile="])
  except getopt.GetoptError:
    error()
  for opt, arg in opts:
    if opt == '-h':
      print 'meterArchivos.py -s <server:luke,test,prod> [-w wait in any directory error] [-r remove old logs]'
      sys.exit()
    elif opt in ["-s","--server"]:
      if serverHash.has_key(arg):
        server = serverHash[arg]
      else:
        print "server: ",arg," not found."
        print "servers accepted: " , reduce(lambda x,y: y+" , "+x,serverHash.keys(),"")[:-2]
        sys.exit(2)
    elif opt == "-r":
        print "Borrando archivos de logs de corridas anteriories"
        for fil in glob.glob('logs/*'):
          os.remove(fil)
    elif opt == '-w':
      wait = True
  if len(argv) == 0 or len(server) == 0:
    error()
  url = server[0]
  urlFind = server[1]
  commandFind = 'find '+server[2]+' -name \'*.png\' -or -name \'*.jpg\' -or -name \'*.gif\''
  userFtp = server[3]
  passFtp = server[4]
  execute(url,urlFind,commandFind,userFtp,passFtp,wait)



if __name__ == "__main__":
  main(sys.argv[1:])
