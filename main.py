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
import cfscrape as cfscrape

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

log = CPLog(__name__)


class torrent9(TorrentProvider, MovieProvider):
    urls = {
        'site': 'http://www.torrent9.bz/',
        'search': 'http://www.torrent9.bz/search_torrent/',
    }

    class NotLoggedInHTTPError(urllib2.HTTPError):
        def __init__(self, url, code, msg, headers, fp):
            urllib2.HTTPError.__init__(self, url, code, msg, headers, fp)

    class PTPHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
        def http_error_302(self, req, fp, code, msg, headers):
            log.debug("302 detected; redirected to %s" % headers['Location'])
            if (headers['Location'] != 'login.php'):
                return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
            else:
                raise torrent9.NotLoggedInHTTPError(req.get_full_url(), code, msg, headers, fp)

    


    def _search(self, movie, quality, results):
        if not self.last_login_check and not self.login():
            return
        TitleStringReal = (getTitle(movie['info']) + ' ' + simplifyString(quality['identifier'] )).replace('-',' ').replace(' ',' ').replace(' ',' ').replace(' ',' ').encode("utf8")
        
        URL = ((self.urls['search'])+TitleStringReal.replace('.', '-').replace(' ', '-')+'.html').encode('UTF8')
        #req = urllib2.Request(URL)
        log.info('opening url %s', URL) 
        #data = urllib2.urlopen(req,timeout=10)
        scraper = cfscrape.create_scraper() 
        data=scraper.get(URL).content 
        #log.info('content %s',data) 
        id = 1000

        if data:
            try:
                html = BeautifulSoup(data)
                torrent_rows = html.findAll('tr')
                 
                for result in torrent_rows:
                    try:
                        if not result.find('a'):
                            continue
                    
                        title = result.find('a').get_text(strip=False)
                        log.info('found title %s',title)

                        testname=namer_check.correctName(title.lower(),movie)
                        if testname==0:
	                    log.info('%s not match %s',(title.lower(),movie['info']['titles']))
		            continue
                        log.info('title %s match',title)

                        tmp = result.find("a")['href'].split('/')[-1].replace('.html', '.torrent').strip()
                        download_url = (self.urls['site'] + 'get_torrent/{0}'.format(tmp) + ".torrent")
                        detail_url = (self.urls['site'] + 'torrent/{0}'.format(tmp))
	                log.debug('download_url %s',download_url)	

                        if not all([title, download_url]):
                            continue

                        seeders = int(result.find(class_="seed_ok").get_text(strip=True))
                        leechers = int(result.find_all('td')[3].get_text(strip=True))
	                size = result.find_all('td')[1].get_text(strip=True)
                    
                        def extra_check(item):
	                    return True
                    
	                size = size.lower()
                        size = size.replace("go", "gb")
                        size = size.replace("mo", "mb")
                        size = size.replace("ko", "kb")
                        size=size.replace(' ','')
                        size=self.parseSize(str(size))
			        
                        new={}		
		        new['id'] = id
		        new['name'] = title.strip()
		        new['url'] = download_url
		        new['detail_url'] = detail_url
		        new['size'] = size
		        new['seeders'] = seeders
		        new['leechers'] = leechers
                        new['extra_check'] = extra_check
		        new['download'] = self.loginDownload  
                        results.append(new)
                        log.info(results)
		        id = id+1
		    except StandardError, e:
                        log.info('boum %s',e)
		        continue
            except AttributeError:
                log.debug('No search results found.')
        else:
            log.debug('No search results found.')

    def login(self):
        return True

    def download(self, url = '', nzb_id = ''):
        log.debug('entering dowload')
        if not self.last_login_check and not self.login():
            return
        log.debug('download %s',url) 
        scraper = cfscrape.create_scraper()
        tokens, user_agent = cfscrape.get_cookie_string(url)
        r_headers={"User-Agent":user_agent,"Cookie":tokens} 
        req = urllib2.Request(url,headers=r_headers)
        try:
            #return scraper.get(url).content()
            return urllib2.urlopen(req).read()
        except:
            log.error('Failed downloading from %s: %s', (self.getName(), traceback.format_exc()))

    loginDownload = download
