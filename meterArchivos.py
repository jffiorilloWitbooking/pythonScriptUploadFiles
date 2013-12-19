#!/usr/bin/python

import pxssh
import getpass
import httplib,urllib,urllib2
import sys
import getopt
import glob,os 
from lxml import etree, html

foldersValid = [ "logo" , "tiposalojamiento" ,  "extras" , "establecimientos" ]
serverHash = {"luke": [
                  "http://luke.local:8080",
                  "luke.local",
                  "/var/www/vhosts/jpala.luke.local/httpdocs/v6/multimedia",
                  "oper",
                  "wIT_oper13"
                ] ,
            "test" : [
                  "http://www3.witbooking.com:8080",
                  "www3.witbooking.com",
                  "/var/www/vhosts/www3.witbooking.com/httpdocs/v6/multimedia/",
                  "root",
                  "WitDevel;"
                ],
            "prod" : [
                  "http://www.witbooking.com:18080",
                  "www.witbooking.com",
                  "httpdocs/v6/multimedia",
                  "ftpwitbooking",
                  "freeRock!708"
                ],
            #, "local" : "localhost"
            }
hasPrinted = False

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
      global hasPrinted
      hasPrinted = True

def incrementInHashMap(hashMap,key):
  if key in hashMap.keys():
    hashMap[key] = hashMap[key]+1
  else:
    hashMap[key] = 1

def sendFile(url,line,lineR,successLog,errorLog,msg,wait,hotelTickerFail,hotelTickerSuccess,rep,new,unknow,verbose,cVerbose):
  try:
    global hasPrinted
    hotelTicker = lineR[0]
    entity = lineR[1]
    idEntity = int(lineR[2])
    fileName = lineR[3]
    params = urllib.urlencode({'hotelTicker':hotelTicker,'entity':entity,'idEntity':idEntity,'fileName':fileName})
    conn= urllib.urlopen(url+"/WitBookerAPI-war/webresources/internal/withotel/insert", params) 
    htmlGet = html.fromstring(conn.read())
    msgBonito=etree.tostring(htmlGet,pretty_print=True)
    successLog.write(str(lineR))
    successLog.write(str(params))
    successLog.write(msgBonito)
    if verbose:
      print lineR
      print params
      print msgBonito
      hasPrinted = True
    if "The database could not be accessed" in msgBonito or "DataBase '"+hotelTicker+"' Not found." in msgBonito:
      if verbose:
        print "hotelTicker "+ hotelTicker + " appended to hotelTickerFail list "
      hotelTickerFail.append(hotelTicker)
    elif "hotelMedia ya existe" in msgBonito:
      rep+=1
      incrementInHashMap(hotelTickerSuccess,hotelTicker)
    elif "HotelMedia{" in msgBonito:
      if cVerbose:
        print lineR
        print params
        print msgBonito
        hasPrinted = True
      new+=1
      incrementInHashMap(hotelTickerSuccess,hotelTicker)
    else:
      unknow+=1
    conn.close()
  except ValueError:
    print msg
    hasPrinted = True
    if (wait):
      raw_input('Error happens, enter any key to continue...')
      hasPrinted = True
    errorLog.write(msg+"\n")
  return [rep,new,unknow]

def execute(url,urlFind,commandFind,userFtp,passFtp,wait,hotelTickerListSelected,verbose,cVerbose):
  print "ssh "+userFtp+"@"+urlFind
  global hasPrinted
  content = getFilesAsString(urlFind,userFtp,passFtp,commandFind)
  errorLog = open('logs/error.log','w')
  successLog = open('logs/success.log','w')
  i = 0
  totalString = content.splitlines(True)[1:]
  hashMap = {}
  hotelTickerFail = []
  successLst = {}
  rep=0
  new=0
  unknow=0
  unsended = 0
  cont = 0
  sizeCont = len(totalString)/20.0
  for line in totalString:
    print line
    showProgress(cont,sizeCont)
    cont +=1
    lineRQ =map(lambda x: x.strip(),line.split("/"))
    msg = "\n"+str(line.strip())+" len: "+str(len(lineRQ))+"\n"
    if len(lineRQ) >= 7 and "multimedia" in lineRQ and lineRQ.index("multimedia")+1 < len(lineRQ):
      lineR = lineRQ[lineRQ.index("multimedia")+1:]
#     lineR = lineRQ[-4:]
      hotelTicker = lineR[0]
      entity = lineR[1]
      if hashMap.has_key(hotelTicker):
        hashMap[hotelTicker] = hashMap[hotelTicker] + 1
      else:
        hashMap[hotelTicker] = 1
      i+=1
      if entity in foldersValid:
        if not hotelTicker in hotelTickerFail and (len(hotelTickerListSelected) == 0 or hotelTicker in hotelTickerListSelected):
          rep,new,unknow = sendFile(url,line,lineR,successLog,errorLog,msg,wait,hotelTickerFail,successLst,rep,new,unknow,verbose,cVerbose)
        else:
          unsended +=1
          errorLog.write("hotelTicker: "+str(hotelTicker)+" found in hotelTickerFail. "+str(lineR)+"\n")
      else:
        unsended +=1
        errorLog.write("entity: "+str(entity)+" not found. "+str(lineR)+"\n")
    else:
      unsended +=1
      hasPrinted = True
      print msg
      errorLog.write(msg+"\n")
  showProgress(cont,sizeCont)
# for hm in hashMap.keys():
#   if not hm in hotelTickerFail and (len(hotelTickerListSelected) == 0 or hm in hotelTickerListSelected):
#     successLst.append(hm)
  print "\ncont " , cont
  msgResumen =  "i : " +  str(i) + " total: " + str(len(totalString))+"\n"
  msgResumen +=  "rep " + str(rep) + " new " + str(new) + " unknow " + str(unknow) +" , unsended "+ str(unsended)+"\n"
  msgResumen +=  "hotelTickerFail " + str(hotelTickerFail) + str(2*"\n")
  msgResumen += "hotelTickerSuccess " + str(successLst) + str(2*"\n")
  msgResumen += "HashMap " + str(hashMap) +"\n"
  print msgResumen
  res = open('logs/resume.report','w')
  res.write(msgResumen)
  res.close()
  errorLog.close()
  successLog.close()

def showProgress(cont,sizeCont):
  global hasPrinted
  if cont > sizeCont:
    if not hasPrinted:
      sys.stdout.write('\r')
    a = float(cont)/sizeCont
    #print 'a : ', a ,'sizeCont' , sizeCont , "cont", cont , 'hasPrinted', hasPrinted
    sys.stdout.write("[%-20s] %d%%" % ('='*int(a), 5*a))
    sys.stdout.flush()
    hasPrinted = False

def error():
  print 'Error, arguments required.'
  showInfo()


def showInfo():
  print './meterArchivos.py -s --server <server:luke,test,prod> [-w wait in any directory error] [-r remove old logs] [-t --hotelTicker hotelTicker] [-v --verbose show everything ] [-c --cVerbose hide ssuccess] [-m multiple hotelTicker separated with spaces] [-f --find grep the lines with the word given]'
  sys.exit()

def main(argv):
  server = []
  wait = False
  verbose = False
  cVerbose = True
  ht = []
  try:
    opts, args = getopt.getopt(argv,"is:rwt:vhm",["server=","hotelTicker=","verbose=","hideSuccessVerbose"])
    #opts, args = getopt.getopt(argv,"hs:o:",["ifile=","ofile="])
  except getopt.GetoptError:
    error()
  for opt, arg in opts:
    if opt == '-i':
      showInfo()
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
    elif opt in [ '-t','--hotelTicker=']:
      ht.append(arg)
    elif opt in ['-v' , '--verbose']:
      verbose=True
    elif opt in ['-h' , '--hideSuccessVerbose']:
      cVerbose=False
    elif opt == '-m':
      ht = ht + arg.split()
  if len(argv) == 0 or len(server) == 0:
    showInfo()
  url = server[0]
  urlFind = server[1]
  commandFind = 'find '+server[2]+' -name \'*.png\' -or -name \'*.jpg\' -or -name \'*.gif\' | grep '+reduce(lambda x,y: x+" -e "+y, foldersValid,"")
  userFtp = server[3]
  passFtp = server[4]
  execute(url,urlFind,commandFind,userFtp,passFtp,wait,ht,verbose,cVerbose)

if __name__ == "__main__":
  main(sys.argv[1:])
