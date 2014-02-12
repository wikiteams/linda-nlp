# coding=UTF-8
'''
Downloads more details about dialogues happening in GitHub.
Now (from version 1.1) includes new GitHub discussion layout
(which changed around 01/02.2014)

@version 1.1
@author Oskar Jarczyk
@since 1.0
@update 06.02.2014
'''

version_name = 'version 1.1 codename: Sonic'
pull_request_filename = 'comments_on_github_2013.csv'

import csv
import scream
import codecs
import cStringIO
import os
import sys
import urllib
import simplejson
import hashlib
import mechanize
from bs4 import BeautifulSoup
import unicodedata


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


def remove_html_markup(s):
    tag = False
    quote = False
    out = ""

    for c in s:
            if c == '<' and not quote:
                tag = True
            elif c == '>' and not quote:
                tag = False
            elif (c == '"' or c == "'") and tag:
                quote = not quote
            elif not tag:
                out = out + c

    return out


latin_letters = {}
symbols = (u"абвгдеёзийклмнопрстуфхъыьэАБВГДЕЁЗИЙКЛМНОПРСТУФХЪЫЬЭ",
           u"abvgdeezijklmnoprstufh'y'eABVGDEEZIJKLMNOPRSTUFH'Y'E")
#tr = {ord(a): ord(b) for a, b in zip(*symbols)}
tr = dict()
#moving to python 2.7.3
for a in zip(*symbols):
    for b in zip(*symbols):
        tr.update({ord(a[0]): ord(b[1])})


def cyrillic2latin(input):
    return input.translate(tr)


def is_latin(uchr):
    try:
        return latin_letters[uchr]
    except KeyError:
        return latin_letters.setdefault(uchr, 'LATIN' in unicodedata.name(uchr))


def only_roman_chars(unistr):
    return all(is_latin(uchr)
               for uchr in unistr
               if uchr.isalpha())  # isalpha suggested by John Machin


def descr_user(s):
    if s in persist_users:
        if persist_users[s] is None:
            return s
        else:
            return persist_users[s]
    #get user name and surname here
    response = urllib.urlopen('https://api.github.com/users/' + s
                              + '?client_id='
                              + client_id + '&client_secret='
                              + client_secret)
    #print response
    data = simplejson.load(response)
    #print data
    #fullname = data['name']
    if 'name' in data:
        fullname = data['name']
    else:
        #print 'fullname not provided'
        persist_users[s] = None
        return s
    if fullname is None:
        #print 'fullname provided but an empty entry'
        persist_users[s] = None
        return s
    if (len(fullname) > 0):
        first_name = unicode(fullname.split()[0])
        if (len(first_name) > 0):
            #ask now internet for gender
            response = my_browser.open('http://genderchecker.com/')
            response.read()
            my_browser.select_form("aspnetForm")
            my_browser.form.set_all_readonly(False)    # allow everything to be written to
            #my_browser.form.set_handle_robots(False)   # ignore robots
            #my_browser.form.set_handle_refresh(False)  # can sometimes hang without this
            #ctl00_TextBoxName
            control = my_browser.form.find_control("ctl00$TextBoxName")
            if only_roman_chars(first_name):
                control.value = first_name.encode('utf-8')
            else:
                control.value = cyrillic2latin(first_name).encode('utf-8')
            #check if value is enough
            #control.text = first_name
            response = my_browser.submit()
            html = response.read()
            local_soup = BeautifulSoup(html)
            failed = local_soup.find("span", {"id": "ctl00_ContentPlaceHolder1_LabelFailedSearchedFor"})
            if failed is not None:
                persist_users[s] = s + ',' + fullname.strip()
                return s + ',' + fullname.strip()
            gender = local_soup.find("span", {"id": "ctl00_ContentPlaceHolder1_LabelGenderFound"}).contents[0].string
            #print gender
            persist_users[s] = s + ',' + fullname.strip() + ',' + gender
            return s + ',' + fullname.strip() + ',' + gender
        else:
            persist_users[s] = s + ',' + fullname.strip()
            return s + ',' + fullname.strip()
    else:
        #print 'fullname not provided'
        persist_users[s] = None
        return s


if __name__ == "__main__":
    scream.say('Start main execution')
    scream.say(version_name)

    #initialize browser for the gender studies :)
    my_browser = mechanize.Browser()
    #my_browser.set_all_readonly(False)    # allow everything to be written to
    my_browser.set_handle_robots(False)   # ignore robots
    my_browser.set_handle_refresh(False)  # can sometimes hang without this
    #end

    if len(sys.argv) < 3:
        print 'OAuth id and/or secret missing, '
        + 'please lunch program with credentials as arguments'
        exit(-1)

    print 'using: ' + sys.argv[1]

    # This information is obtained upon registration of a new GitHub
    client_id = sys.argv[1]
    client_secret = sys.argv[2]

    persist_md5 = dict()
    persist_users = dict()

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

            local_filename, headers = urllib.urlretrieve(key + '?client_id='
                                                         + client_id + '&client_secret='
                                                         + client_secret, filename + '.json')

            with open(local_filename, 'r') as content_file:
                json = simplejson.load(content_file)
                if (len(json) < 3) and (json['message'] == 'Not Found'):
                    print 'Pull request dont exist anymore'
                else:
                    html_addr = json['html_url']
                    local_filename_html, headers_html = urllib.urlretrieve(
                        html_addr, filename + '.html')
                    # btw, whats the html result code here ?
                    print 'File downloaded, lets get to scrapping dialogues from there..'
                    with codecs.open(filename + '.txt', 'wb', 'utf-8') as result_txt_file:
                        with open(local_filename_html, 'r') as html_content_file:
                            soup = BeautifulSoup(html_content_file)
                            #discussion_title = soup.find("h2", {"class": "discussion-topic-title js-comment-body-title"}).contents[0]
                            #github changed to a new tag:
                            title_h1 = soup.find("h1", {"class": "gh-header-title"})
                            time = 60
                            if title_h1 is None:
                                #retry 3 times
                                for i in range(0,3):
                                    time.sleep(time)
                                    time *= 3
                                    local_filename_html, headers_html = urllib.urlretrieve(
                                        html_addr, filename + '.html')
                                    soup = BeautifulSoup(html_content_file)
                                    title_h1 = soup.find("h1", {"class": "gh-header-title"})
                                    if title_h1 is not None:
                                        break
                            if title_h1 is None:
                                #nothing to do here, lets move on
                                print 'orphaned' + filename + '.json'
                                print filename + '.json' + 'is without proper html. GitHub not responding or giving 404/501 erorr ??'
                                continue
                            discussion_title = title_h1.find("span", {"class": "js-issue-title"}).contents[0] + title_h1.find(
                                "span", {"class": "gh-header-number"}).contents[0]
                            #discussion_initiator = soup.find("span", {"class": "discussion-topic-author"}).contents[0].contents[0]
                            #github changed to a new tag:
                            discussion_initiator = soup.find("a", {
                                "class": "author pull-header-username css-truncate css-truncate-target expandable"}).contents[0].strip()
                            result_txt_file.write(u'-[' + descr_user(unicode(discussion_initiator)) + u']' + os.linesep)
                            result_txt_file.write(u'[' + discussion_title + u']' + os.linesep + os.linesep)
                            #first_sentence = soup.findAll("div", {"class": "js-comment-body comment-body markdown-body markdown-format"})[0].contents[1]
                            #result_txt_file.write(unicode(first_sentence) + os.linesep)
                            #in new discussion layout there is no need to parse seperatly "first sentence"
                            #for candidate in soup.findAll("div", {"class": "timeline-comment timeline-comment-"}):
                            #    result_txt_file.write(os.linesep)
                            #    author = candidate.find("a", {"class": "author"}).contents[0]
                            #    result_txt_file.write(u'-[' + author + u']' + os.linesep)
                            #    sentence_search = candidate.find("div", {"class": "comment-body markdown-body markdown-format js-comment-body"})
                            #    if sentence_search is not None:
                            #        sentence = sentence_search.contents[1:-1]
                            #        for s in sentence:
                            #            tag = str(s).strip()
                            #            if ( (len(tag) > 1) and (tag != 'None')):
                            #                result_txt_file.write(unicode(remove_html_markup(tag).decode('utf-8')) + os.linesep)
                                    #result_txt_file.write(os.linesep)
                            for candidate in soup.findAll("div", {"class": "comment js-comment js-task-list-container"}):
                                author = candidate.find("a", {"class": "author"}).contents[0]
                                result_txt_file.write(u'-[' + descr_user(unicode(author)) + u']' + os.linesep)
                                sentence_search = candidate.find("div", {"class": "comment-body markdown-body markdown-format js-comment-body"})
                                if sentence_search is not None:
                                    sentence = sentence_search.contents[1:-1]
                                    for s in sentence:
                                        tag = str(s).strip()
                                        if ( (len(tag) > 1) and (tag != 'None')):
                                            result_txt_file.write(unicode(remove_html_markup(tag), 'utf-8') + os.linesep)
                                email_search = candidate.find("div", {"class": "comment-body markdown-body email-format js-comment-body"})
                                if email_search is not None:
                                    sentence = email_search.contents[1:-1]
                                    for s in sentence:
                                        tag = str(s).strip()
                                        if ( (len(tag) > 1) and (tag != 'None')):
                                            result_txt_file.write(unicode(remove_html_markup(tag), 'utf-8') + os.linesep)
                        result_txt_file.close()

                    hexi = hashlib.md5(open(filename + '.txt').read()).hexdigest()
                    if hexi in persist_md5:
                        print 'Duplicated!'
                        os.remove(filename + '.txt')
                    else:
                        print 'A new dialog confirmed.'
                        persist_md5[hexi] = filename + '.txt'

            print 'Moving next'
