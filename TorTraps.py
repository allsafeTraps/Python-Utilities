
import requests
import json
import logging
import datetime
import pandas as pd
from bs4 import BeautifulSoup
import os

import argparse


HEADERS_REQUESTS = {'Accept-Encoding': 'gzip, deflate',
                    'User-Agent': 'TOR_TRAPS',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Te': 'trailers',
                    'Connection': 'close'
                    }

PROXIES = {
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'
          }

DANIEL_HOSTING = 'http://donionsixbjtiohce24abfgsffo2l4tk26qx464zylumgejukfq2vead.onion/onions.php?format=json'   
AHMIA_HOSTING = 'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/onions/'

logging.basicConfig(filename='TorTraps.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
         
FileDate = datetime.datetime.now()


def functionCallMethod():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--daniel", action='store_true', help="Method to call Daniel Hosting API")
    parser.add_argument("-ah", "--ahmia", action='store_true', help="Method to call Ahmia API")
    parser.add_argument("-all", "--allmethods", action='store_true', help="Method to call Ahmia and Daniel hosting API")
    parser.add_argument("-find", "--findRelations", action='store_true', help="Method to find relations between hosting Domains")
    
    args = parser.parse_args()
    
    if args.daniel:
        DanielHostingOnionDomains()
    elif args.ahmia:
        AhmiaOnionDomains()
    elif args.allmethods:
        DanielHostingOnionDomains()
        AhmiaOnionDomains()
    elif args.findRelations:
        RelationsApiOnionDomainsDanielHosting()   
    else:
        print("usage: python3 Tor_Traps.py [-h] for to select correct method")     



#Request_Find_Relantions
def RelationsApiOnionDomainsDanielHosting():
    
    try:
        
        logging.info("FIND_RELATIONS")
        file_exists = os.path.exists('FindRelations.txt')
        if file_exists:
            f = open("FindRelations.txt", "r")
            for x in f:
                x = x.replace('\n','')
                print(x)
                onionDomain = checkActiveDomain(x)
                if onionDomain:
                    if(onionDomain.status_code == 200):
                        soup = BeautifulSoup(onionDomain.text, 'html.parser')
                        for a in soup.find_all('a', href=True):
                            if('http' in a['href']):
                                print ("Found the URL:", a['href'])
                                relationsFile = open(FileDate.strftime('%d_%m_%Y_%H_%M_%S')+"_RelationsDomains.csv","a")
                                relationsFile.write("%s,%s" % (x, a['href']))
                                relationsFile.write('\n ')    
                else:
                    logging.warning("URL_DOWN")    
    
    
        
    except Exception as inst:
        print(type(inst))   
        print(inst.args)    
        print(inst)
        logging.error(inst)   


#Request_From_Daniel_Hosting
def DanielHostingOnionDomains():
    
    try:
            
            logging.info("DANIEL HOSTING SOURCE")
            danielHostingRequest = onionsSessions().get(DANIEL_HOSTING, headers = HEADERS_REQUESTS, timeout = 30, verify = False)
            if(danielHostingRequest.status_code == 200):
                jsonDanielHosting = json.loads(danielHostingRequest.text)
                #EXPORT_TO_CSV_FILE
                danielHostingCSVFile = open(FileDate.strftime('%d_%m_%Y_%H_%M_%S')+"_DanielHosting.csv","a")
                df = pd.json_normalize(jsonDanielHosting['onions'])
                logging.info("GENERATE FILE: %s" % danielHostingCSVFile)
                df.to_csv(danielHostingCSVFile) 
        
    except requests.Timeout:
            logging.error("TIMEOUT")
        
    except Exception as inst:
        print(type(inst))   
        print(inst.args)    
        print(inst)
        logging.error(inst)
    
    finally:
        danielHostingCSVFile.close()
        
#Request_From_Daniel_Hosting
def AhmiaOnionDomains():
            
    try:
        
        logging.info('AHMIA API')
        onionsSessions()
        AhmiaHostingRequest = onionsSessions().get(AHMIA_HOSTING, headers = HEADERS_REQUESTS, timeout = 30, verify = False)
        if(AhmiaHostingRequest.status_code == 200):
            logging.info('PARSER_URLS')
            #EXPORT_TO_CSV_FILE
            ahmiaHostingCSVFile = open(FileDate.strftime('%d_%m_%Y_%H_%M_%S')+"_AhmiaHosting.csv","a")
            #As ahmia does not has category, it is necessary to check all urls one to one
            for ahmiaUrl in AhmiaHostingRequest.text.split('<br>'):
                #CHECK_DOMAIN_IS_ACTIVE
                responseAhmiaDomain = checkActiveDomain(ahmiaUrl)
                if(responseAhmiaDomain != False and responseAhmiaDomain.status_code == 200):
                    soup = BeautifulSoup(responseAhmiaDomain.text, 'html.parser')
                    
                    titleAhmiaRequest = soup.find('title')
                    if hasattr(titleAhmiaRequest, 'renderContents'):
                        ahmiaHostingCSVFile.write(str(ahmiaUrl)+','+str(titleAhmiaRequest.renderContents()))
                        ahmiaHostingCSVFile.write('\n ')
                    else:
                        ahmiaHostingCSVFile.write(str(ahmiaUrl)+','+str(responseAhmiaDomain.text))
                        ahmiaHostingCSVFile.write('\n ')
                
                    
    except requests.Timeout:
        logging.error("TIMEOUT")
        
    except Exception as inst:
        print(type(inst))   
        print(inst.args)    
        print(inst)
        logging.error(inst)
    finally:
        ahmiaHostingCSVFile.close()     
        
              
def onionsSessions():
    session= requests.Session()
    session.proxies = {}
    session.proxies['http'] = 'socks5h://localhost:9050'
    session.proxies['https'] = 'socks5h://localhost:9050'
    return session            
  
#SE COMPRUEBA QUE EL DOMINIO ESTE ACTIVO 
def checkActiveDomain(url):              
     
    try:
        
        ahmiaParserHtmlCode = onionsSessions().get(url, headers = HEADERS_REQUESTS, timeout = 8, verify = False)

        return ahmiaParserHtmlCode
    
    except requests.Timeout:
        logging.error("TIMEOUT_DOMAIN_INACTIVE: %s" % url)
        return False
    
    except Exception:
        logging.warning("DOMAIN INACTIVE: %s" % url)
        return False        
    
if __name__ == '__main__':
    functionCallMethod()
    #AhmiaOnionDomains()
    #RelationsApiOnionDomainsDanielHosting()
