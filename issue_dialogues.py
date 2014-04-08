# coding=UTF-8
'''
Downloads more details about dialogues held under issues in GitHub.
Now (from version 1.1) includes new GitHub discussion layout
(which changed around 01/02.2014)

@version 1.2.0408
@author Oskar Jarczyk
@since 1.0
@update 8.04.2014
'''

version_name = 'version 1.2 codename: Thorne-Zytkow'
top_repos_filename = 'result_stargazers_2013_final_mature.csv'

import csv
import scream
import logmissed
import codecs
import cStringIO
import os
import sys
import urllib
import urllib2
import simplejson
import hashlib
import mechanize
import time
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
    quoting = csv.QUOTE_ALL
    delimiter = ';'
    escapechar = '\\'
    quotechar = '"'
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
        return latin_letters.setdefault(uchr,
                                        'LATIN' in unicodedata.name(uchr))


def only_roman_chars(unistr):
    return all(is_latin(uchr)
               for uchr in unistr
               if uchr.isalpha())  # isalpha suggested by John Machin


def StripNonAlpha(s):
    return "".join(c for c in s if c.isalpha())


def descr_user(s):
    if s in persist_users:
        if persist_users[s] is None:
            return s
        else:
            return persist_users[s]
    #get user name and surname here
    while True:
        try:
            response = urllib.urlopen('https://api.github.com/users/' + s
                                      + '?token=' + client_token + '?client_id='
                                      + client_id + '&client_secret='
                                      + client_secret)
            break
        except IOError:
            print 'API GitHub not responding, urlopen failed'
            print 'retrying after 1 minute'
            time.sleep(60)
    scream.ssay(response)
    data = simplejson.load(response)
    scream.ssay(data)
    #fullname = data['name']
    if 'name' in data:
        fullname = data['name']
    else:
        scream.say('Fullname not provided')
        persist_users[s] = None
        return s
    if fullname is None:
        scream.say('Fullname provided but an empty entry')
        persist_users[s] = None
        return s
    if (len(fullname) > 0):
        first_name = unicode(fullname.split()[0])
        if (len(first_name) > 0):
            scream.say('#ask now internet for gender')
            submit_retry_counter = 240
            while True:
                try:
                    response = my_browser.open('http://genderchecker.com/')
                    response.read()
                    scream.say('Response read. Mechanize selecting form.')
                    my_browser.select_form("aspnetForm")
                    my_browser.form.set_all_readonly(False)
                    # allow everything to be written
                    control = my_browser.form.find_control("ctl00$TextBoxName")
                    #check if value is enough
                    #control.text = first_name
                    scream.say('Control value is set to :' + str(control.value))
                    if only_roman_chars(first_name):
                        control.value = StripNonAlpha(first_name.encode('utf-8'))
                    else:
                        control.value = StripNonAlpha(cyrillic2latin(first_name).encode('utf-8'))
                    response = my_browser.submit()
                    html = response.read()
                    break
                except urllib2.URLError:
                    scream.ssay('Site genderchecker.com seems to be down' +
                                '. awaiting for 60s before retry')
                    time.sleep(60)
                except mechanize.HTTPError, e:
                    submit_retry_counter -= 1
                    if submit_retry_counter < 1:
                        break
                    error_message = 'Site genderchecker.com seems to have ' +\
                                    'internal problems. or my request is' +\
                                    ' wibbly-wobbly nonsense. HTTPError ' +\
                                    str(e.code) +\
                                    '. awaiting for 60s before retry'
                    scream.say(error_message)
                    scream.log_error(str(e.code) + ': ' + error_message)
                    time.sleep(60)
                except:
                    submit_retry_counter -= 1
                    if submit_retry_counter < 1:
                        break
                    error_message = 'Site genderchecker.com seems to have ' +\
                                    'internal problems. or my request is' +\
                                    ' wibbly-wobbly nonsense. ' +\
                                    'awaiting for 60s before retry'
                    scream.say(error_message)
                    scream.log_error(error_message)
                    time.sleep(60)
            local_soup = BeautifulSoup(html)
            failed = local_soup.find("span",
                                     {"id":
                                      "ctl00_ContentPlaceHolder1_" +
                                      "LabelFailedSearchedFor"})
            if failed is not None:
                persist_users[s] = s + ',' + fullname.strip()
                return s + ',' + fullname.strip()
            gender_tag = local_soup.find("span",
                                         {"id":
                                         "ctl00_ContentPlaceHolder1_" +
                                         "LabelGenderFound"})
            if ((gender_tag is not None) and (gender_tag.contents is not None) and (len(gender_tag.contents) > 0)):
                gender = gender_tag.contents[0].string
                scream.say(gender)
                persist_users[s] = s + ',' + fullname.strip() + ',' + gender
                return s + ',' + fullname.strip() + ',' + gender
            else:
                scream.log_warning('Something really wrong, on result page there ' +
                                   'was no not-found label neither a proper result')
                persist_users[s] = s + ',' + fullname.strip()
                return s + ',' + fullname.strip()
        else:
            persist_users[s] = s + ',' + fullname.strip()
            return s + ',' + fullname.strip()
    else:
        scream.say('Fullname not provided')
        persist_users[s] = None
        return s


# This method tries to get HTML discussion site again again
# when there is a problem with finding by th BS
# proper html tags which allways indicate author
# or discussion content - a must content to exist
def retry_if_neccessary(gotten_tag, tagname, objectname, arg_objectname):
    how_long = 60
    if gotten_tag is None:
        #retry 3 times
        for i in range(0, 3):
            time.sleep(how_long)
            how_long *= 3

            while True:
                try:
                    local_filename_html, headers_html = urllib.urlretrieve(
                        html_addr, filename_with_issue_id + '.html')
                    break
                except IOError:
                    io_socket_message = 'Socket error while retrieving HTML' +\
                                        ' file from GitHub! Internet or ' +\
                                        'GitHub down? Retry after 1 minute'
                    scream.ssay(io_socket_message)
                    scream.log_warning(io_socket_message)
                    time.sleep(60)

            soup = BeautifulSoup(html_content_file)
            gotten_tag = soup.find(tagname, {objectname: arg_objectname})
            if gotten_tag is not None:
                break  # raise StopIteration maybe would be better but break is enough
        if gotten_tag is None:
            #nothing to do here, lets move on
            scream.ssay('orphaned' + filename + '.json')
            scream.log_error(filename + '.json' + 'is without proper html. ' +
                             'GitHub not responding or giving 404/501 erorr ??')
            return None
    scream.say('No action required. retry_if_neccessary() returning gotten_tag')
    return gotten_tag


if __name__ == "__main__":
    scream.say('--- Start main execution ---')
    scream.say(version_name)

    ACCOUNT_REMOVED_LABEL = '__ACCOUNT_DELETED'
    scream.intelliTag_verbose = True
    logmissed.intelliDialogue_verbose = True

    #initialize browser for the gender studies :)
    my_browser = mechanize.Browser()
    #my_browser.set_all_readonly(False)    # allow everything to be written to
    my_browser.set_handle_robots(False)   # ignore robots
    my_browser.set_handle_refresh(False)  # can sometimes hang without this
    #end

    resume_from_entity = None

    if len(sys.argv) < 4:
        scream.say('Token, OAuth id and/or secret missing, '
                   + 'please lunch program with credentials as arguments')
        exit(-1)
    if len(sys.argv) > 5:
        scream.say('Too many arguments provided. Check manual and try again')
        exit(-1)
    if len(sys.argv) == 5:
        resume_from_entity = sys.argv[4].strip()

    scream.say('using client_id: ' + sys.argv[2])

    sys.setrecursionlimit(2000)

    # This information is obtained upon registration of a new GitHub
    client_token = sys.argv[1]
    client_id = sys.argv[2]
    client_secret = sys.argv[3]

    persist_md5 = dict()
    persist_users = dict()

    with open(top_repos_filename, 'rb') as source_csvfile:
        reposReader = UnicodeReader(source_csvfile)
        reposReader.next()
        for row in reposReader:
            try:
                url = str(row[1])
            except IndexError:
                print 'IndexError when processing repourl:'
                logmissed.error(row)
                continue
            scream.say('Working on repository ' + url)

            repoowner = str(row[0])
            reponame = str(row[2])
            #issuenumber = key.split('/')[8]

            filename = 'issue' + '#' + repoowner + '#' + reponame + '#'
            guess_iterator_beginning = 1

            if resume_from_entity is not None:
                guess_iterator_beginning = int(resume_from_entity.split('#')[3])
                if filename + str(guess_iterator_beginning) == resume_from_entity:
                    scream.say('Found! Resuming work.')
                    resume_from_entity = None
                else:
                    continue

            with open(filename + 'all.log', 'wb') as log_file:
                mark_404 = None
                for guess_iterator in range(guess_iterator_beginning, 500000):
                    html_addr = url + '/issues/' + str(guess_iterator)
                    filename_with_issue_id = filename + str(guess_iterator)
                    while True:
                        try:
                            local_filename_html, headers_html = urllib.urlretrieve(
                                html_addr, filename_with_issue_id + '.html')
                            break
                        except IOError:
                            scream.say('GitHub page not responding, problem with GitHub, try again')
                            time.sleep(30)
                    scream.say('File downloaded, lets get to scrapping dialogues from there..')
                    with codecs.open(filename + str(guess_iterator) + '.txt', 'wb', 'utf-8') as result_txt_file:
                        with open(local_filename_html, 'r') as html_content_file:
                            soup = BeautifulSoup(html_content_file)
                            # btw, whats the html result code here ?
                            title_html_error = soup.find("img", {"id": "parallax_error_text"})
                            if title_html_error is not None:
                                scream.say('Issues no more there are! quit for this repo..')
                                mark_404 = filename + str(guess_iterator) + '.txt'
                                break
                            #github changed to a new tag:
                            title_h1 = soup.find("h1", {"class": "gh-header-title"})
                            title_h1 = retry_if_neccessary(title_h1, "h1", "class", "gh-header-title")
                            if title_h1 is None:
                                continue
                            discussion_title = title_h1.find("span", {"class": "js-issue-title"}).contents[0] + title_h1.find(
                                "span", {"class": "gh-header-number"}).contents[0]
                            scream.say('discussion_title received')
                            #github changed to a new tag:
                            discussion_initiator_diva = soup.find("div", {
                                "class": "gh-header-meta"})
                            discussion_initiator_diva = retry_if_neccessary(discussion_initiator_diva, "div",
                                                                         "class",
                                                                         "gh-header-meta")
                            discussion_initiator_pull = discussion_initiator_diva.findAll("span", {
                                "class": "css-truncate-target user"})
                            discussion_initiator_issue = discussion_initiator_diva.find("a", {
                                "class": "author"})
                            if discussion_initiator_issue is None:
                                scream.say(discussion_initiator_pull)
                                if len(discussion_initiator_pull) > 0:
                                    discussion_initiator_a = discussion_initiator_pull[-1]
                                else:
                                    discussion_initiator_a = repoowner
                            else:
                                discussion_initiator_a = discussion_initiator_issue
                            #scream.say('discussion_initiator is: ' + discussion_initiator_a)
                            
                            if discussion_initiator_a is None:
                                continue
                            if isinstance(discussion_initiator_a, str):
                                discussion_initiator = discussion_initiator_a
                            else:
                                discussion_initiator = discussion_initiator_a.contents[0].strip()
                            scream.say('Describing user: ' + discussion_initiator + ' unicode: ' + unicode(discussion_initiator))
                            result_txt_file.write(u'-[' + descr_user(unicode(discussion_initiator)) + u']' + os.linesep)
                            result_txt_file.write(u'[' + discussion_title + u']' + os.linesep + os.linesep)

                            for candidate in soup.findAll("div", {"class": "comment js-comment js-task-list-container"}):
                                scream.say(str(candidate))
                                #scream.say(str(candidate.contents))
                                author_is_deleted = candidate.find("span", {"aria-label": "Oops! This commit is missing author information."})
                                if author_is_deleted is None:
                                    author = candidate.find("a", {"class": "author"})
                                    author = retry_if_neccessary(author, "a", "class", "author")
                                    if author is None:
                                        continue
                                    else:
                                        author = author.contents[0]
                                    scream.say('Describing user (inside candiate loop): ' + author + ' unicode: ' + unicode(author))
                                    result_txt_file.write(u'-[' + descr_user(unicode(author)) + u']' + os.linesep)
                                    scream.say('User described and result line written')
                                else:
                                    scream.say('Authors github account was deleted permanently')
                                    result_txt_file.write(u'-[' + ACCOUNT_REMOVED_LABEL + u']' + os.linesep)
                                sentence_search = candidate.find("div", {"class": "comment-body markdown-body markdown-format js-comment-body"})
                                if sentence_search is not None:
                                    sentence = sentence_search.contents[1:-1]
                                    for s in sentence:
                                        tag = unicode(s).strip().encode('utf-8')
                                        if ((len(tag) > 1) and (tag != 'None')):
                                            result_txt_file.write(unicode(remove_html_markup(tag), 'utf-8') + os.linesep)
                                scream.say('sentence_search loop passed')
                                email_search = candidate.find("div", {"class": "comment-body markdown-body email-format js-comment-body"})
                                if email_search is not None:
                                    sentence = email_search.contents[1:-1]
                                    for s in sentence:
                                        tag = unicode(s).strip().encode('utf-8')
                                        if ((len(tag) > 1) and (tag != 'None')):
                                            result_txt_file.write(unicode(remove_html_markup(tag), 'utf-8') + os.linesep)
                                scream.say('email_search loop passed')
                        scream.say('Closing result file')
                        result_txt_file.close()
                        scream.say('Result file closed')

                    scream.say('Checking md5')
                    hexi = hashlib.md5(open(filename + str(guess_iterator) + '.txt').read()).hexdigest()
                    scream.say(str(hexi))
                    if hexi in persist_md5:
                        scream.say('Duplicated!')
                        os.remove(filename + str(guess_iterator) + '.txt')
                    else:
                        scream.say('A new dialog confirmed.')
                        persist_md5[hexi] = filename + str(guess_iterator) + '.txt'
                if mark_404 is not None:
                    log_file.write('Ids finished on ' + mark_404)
                    os.remove(mark_404)

            scream.say('Moving next')
