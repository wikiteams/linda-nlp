'''
Downloads more details about dialogues happening in GitHub

@since 1.0
@author Oskar Jarczyk

@update 17.01.2014
'''

version_name = 'version 1.0 codename: Gallifrey'
pull_request_filename = 'comments_on_github_2013.csv'

import csv
import scream
import codecs
import cStringIO
import __builtin__
import os
import sys
import urllib
import simplejson
from bs4 import BeautifulSoup
from requests_oauthlib import OAuth2Session


class MyDialect(csv.Dialect):
    strict = True
    skipinitialspace = True
    quoting = csv.QUOTE_MINIMAL
    delimiter = ','
    escapechar = '\\'
    quotechar = '"'
    lineterminator = '\n'


class ReadDialect(csv.Dialect):
    strict = True
    skipinitialspace = False
    quoting = csv.QUOTE_NONE
    delimiter = ','
    escapechar = '\\'
    lineterminator = '\n'


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=ReadDialect, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=MyDialect, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

if __name__ == "__main__":
    scream.say('Start main execution')
    scream.say(version_name)

    print 'using: ' + sys.argv[1]

    # This information is obtained upon registration of a new GitHub
    client_id = sys.argv[1]
    client_secret = sys.argv[2]
    #authorization_base_url = 'https://github.com/login/oauth/authorize'
    #token_url = 'https://github.com/login/oauth/access_token'

    #github = OAuth2Session(client_id, state=session['oauth_state'])
    #token = github.fetch_token(token_url, client_secret=client_secret,
    #authorization_response=request.url)

    with open(pull_request_filename, 'rb') as source_csvfile:
        reposReader = UnicodeReader(source_csvfile)
        reposReader.next()
        for row in reposReader:
            key = str(row[10])
            print 'Working on comment ' + key

            repoowner = str(row[7])
            reponame = key.split('/')[5]
            pullnumber = key.split('/')[8]

            filename = 'pull' + '#' + repoowner + '#' + reponame + '#' + pullnumber

            local_filename, headers = urllib.urlretrieve(key + '?client_id=' + client_id + '&client_secret=' + client_secret, filename + '.json')
            #better with authentication
            #local_filename = filename + '.json'
            #response = client.get(key)
            #fjson = open(local_filename, 'wb')
            #fjson.write(response.content)
            #fjson.close
            with open(local_filename, 'r') as content_file:
                #content = content_file.read()
                #print content
                json = simplejson.load(content_file)
                if (len(json) < 3) and (json['message'] == 'Not Found'):
                    print 'Pull request dont exist anymore'
                else:
                    html_addr = json['html_url']
                    local_filename_html, headers_html = urllib.urlretrieve(html_addr, filename + '.html')
                    # btw, whats the html result code here ?
                    print 'File downloaded, lets get to scrapping dialogues from there..'
                    with codecs.open(filename + '.txt', 'wb', 'utf-8') as result_txt_file:
                        #result_txt_file.write('\n')
                        with open(local_filename_html, 'r') as html_content_file:
                            soup = BeautifulSoup(html_content_file)
                            discussion_title = soup.find("h2", {"class": "discussion-topic-title js-comment-body-title"}).contents[0]
                            discussion_initiator = soup.find("span", {"class": "discussion-topic-author"}).contents[0].contents[0]
                            result_txt_file.write(u'[' + discussion_title + u']' + os.linesep)
                            result_txt_file.write(u'-[' + discussion_initiator + u']' + os.linesep)
                            first_sentence = soup.findAll("div", {"class": "js-comment-body comment-body markdown-body markdown-format"})[0].contents[1]
                            result_txt_file.write(unicode(first_sentence) + os.linesep)
                            for candidate in soup.findAll("div", {"class": "comment-header -comment-header"}):
                                author = candidate.find("a", {"class": "comment-header-author"}).contents[0]
                                result_txt_file.write(u'-[' + author + u']' + os.linesep)
                                sentence = candidate.parent.find("div", {"class": "js-comment-body comment-body markdown-body markdown-format"}).contents[1]
                                result_txt_file.write(unicode(sentence) + os.linesep)
                        result_txt_file.close()

            print 'Moving next'
