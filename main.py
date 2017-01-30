from bs4 import BeautifulSoup
from couchpotato.core.helpers.variable import getTitle, tryInt
from couchpotato.core.logger import CPLog
from couchpotato.core.helpers.encoding import simplifyString, tryUrlencode
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider
from couchpotato.core.media.movie.providers.base import MovieProvider
import cookielib
import re
import traceback
import urllib
import urllib2
import unicodedata
from couchpotato.core.helpers import namer_check


import sys

reload(sys)
sys.setdefaultencoding('utf-8')

log = CPLog(__name__)


class torrent9(TorrentProvider, MovieProvider):
    urls = {
        'test': 'http://www.torrent9.biz/',
        'search': 'http://www.torrent9.biz/search_torrent/',
    }

    http_time_between_calls = 2 #seconds
    cat_backup_id = None

    class NotLoggedInHTTPError(urllib2.HTTPError):
        def __init__(self, url, code, msg, headers, fp):
            urllib2.HTTPError.__init__(self, url, code, msg, headers, fp)

    class PTPHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
        def http_error_302(self, req, fp, code, msg, headers):
            log.debug("302 detected; redirected to %s" % headers['Location'])
            if (headers['Location'] != 'login.php'):
                return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
            else:
                raise cpasbien.NotLoggedInHTTPError(req.get_full_url(), code, msg, headers, fp)

    def _search(self, movie, quality, results):

                # Cookie login
        if not self.last_login_check and not self.login():
            return


        TitleStringReal = (getTitle(movie['info']) + ' ' + simplifyString(quality['identifier'] )).replace('-',' ').replace(' ',' ').replace(' ',' ').replace(' ',' ').encode("utf8")
        
        URL = ((self.urls['search'])+TitleStringReal+'.html').encode('UTF8')

        req = urllib2.Request(URL)
        log.info('sending to %s', URL) 
        data = urllib2.urlopen(req,timeout=10)
       
        id = 1000

        if data:
                       
            try:
                html = BeautifulSoup(data)
                lin=0
                erlin=0
                resultdiv=[]
                while erlin==0:
                    try:
                        classlin='ligne'+str(lin)
                        resultlin=html.findAll(attrs = {'class' : [classlin]})
                        if resultlin:
                            for ele in resultlin:
                                resultdiv.append(ele)
                            lin+=1
                        else:
                            erlin=1
                    except:
                        erlin=1
                for result in resultdiv:

                    try:
                        
                        new = {}
                        name = result.findAll(attrs = {'class' : ["titre"]})[0].text
                        testname=namer_check.correctName(name,movie)
                        if testname==0:
                            continue
                        detail_url = result.find("a")['href']
                        tmp = detail_url.split('/')[-1].replace('.html','.torrent')
                        url_download = ('http://www.cpasbien.cm/telechargement/%s' % tmp)
                        size = result.findAll(attrs = {'class' : ["poid"]})[0].text.replace('Go', 'Gb').replace('Mo', 'Mb')
                        seeder = result.findAll(attrs = {'class' : ["seed_ok"]})[0].text
                        leecher = result.findAll(attrs = {'class' : ["down"]})[0].text
                        age = '1'

                        verify = getTitle(movie['info']).split(' ')
                        
                        add = 1
                        
                        for verify_unit in verify:
                            if (name.lower().find(verify_unit.lower()) == -1) :
                                add = 0

                        def extra_check(item):
                            return True

                        if add == 1:

                            new['id'] = id
                            new['name'] = name.strip()
                            new['url'] = url_download
                            new['detail_url'] = detail_url
                            new['size'] = self.parseSize(size)
                            new['age'] = self.ageToDays(str(age))
                            new['seeders'] = tryInt(seeder)
                            new['leechers'] = tryInt(leecher)
                            new['extra_check'] = extra_check
                            new['download'] = self.loginDownload             
    
                            #new['score'] = fireEvent('score.calculate', new, movie, single = True)
    
                            #log.error('score')
                            #log.error(new['score'])
    
                            results.append(new)
    
                            id = id+1
                        
                    except:
                        log.error('Failed parsing cPASbien: %s', traceback.format_exc())

            except AttributeError:
                log.debug('No search results found.')
        else:
            log.debug('No search results found.')

    def ageToDays(self, age_str):
        age = 0
        age_str = age_str.replace('&nbsp;', ' ')

        regex = '(\d*.?\d+).(sec|heure|jour|semaine|mois|ans)+'
        matches = re.findall(regex, age_str)
        for match in matches:
            nr, size = match
            mult = 1
            if size == 'semaine':
                mult = 7
            elif size == 'mois':
                mult = 30.5
            elif size == 'ans':
                mult = 365

            age += tryInt(nr) * mult

        return tryInt(age)

    def login(self):
	log.debug('Try to login on torrent9')
	return True
        
    def loginDownload(self, url = '', nzb_id = ''):
        values = {
          'url' : '/'
        }
        data_tmp = urllib.urlencode(values)
        req = urllib2.Request(url, data_tmp, headers={'User-Agent' : "Mozilla/5.0"} )
        
        try:
            if not self.last_login_check and not self.login():
                log.error('Failed downloading from %s', self.getName())
            return urllib2.urlopen(req).read()
        except:
            log.error('Failed downloading from %s: %s', (self.getName(), traceback.format_exc()))
            
    def download(self, url = '', nzb_id = ''):
        
        if not self.last_login_check and not self.login():
            return
        
        values = {
          'url' : '/'
        }
        data_tmp = urllib.urlencode(values)
        req = urllib2.Request(url, data_tmp, headers={'User-Agent' : "Mozilla/5.0"} )
        
        try:
            return urllib2.urlopen(req).read()
        except:
            log.error('Failed downloading from %s: %s', (self.getName(), traceback.format_exc()))
			
