linda-nlp
=========

### **Recognizing dialog acts on GitHub 2013/2014**
*lindo m (feminine linda, masculine plural lindi, feminine plural linde); neat, clean, tidy*

#### The purpose of this program is to create a corpo for language analyzis of GitHub *discussions* held during year 2013, for further NLP analysis using external tools. Corpo is first annotated with **Brat** annotation tools, than we use a machine learning solutions to predict diaog acts on rest of the dataset.

**License**

The MIT License (MIT)

Copyright (c) 2013 Oskar Jarczyk / WikiTeams.pl

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


**Program goal**

Script creates a dataset of all GitHub-held dialogues which happened during past year. Moreover, gender of the sentence author is being guessed - which can make for further gender-alike analysis. But the main goal is to tag the dataset with dialog acts (like i.e. criticism, information providing, etc.). Finally, it will allow to associate particular dialog acts with repository quality and make word-clouds on demand.


**Usage description**

It's a command prompt program, requires Python 2.7+

```
python pullrequest.py client_oath_id client_secret
python issue_dialogues.py client_oath_id client_secret
```

or unix nohup version

```
nohup python pullrequest.py client_oath_id client_secret > logs.txt &
nohup python issue_dialogues.py client_oath_id client_secret > logs.txt &
```

if you need to resume from a step, add additional argument at pos 3:

```
nohup python pullrequest.py client_oath_id client_secret pull#repoowner#reponame#pullnumber > logs.txt &
nohup python issue_dialogues.py client_oath_id client_secret issue#repoowner#reponame > logs.txt &
```

Be advised, that GitHub quota mechanism may apply and cut you from downloading through urllib and API.

PS: You can run Python with the **-u flag** to avoid output buffering

**Required data**

You will need to place a dataset .csv file which you can download from here: https://dl.dropboxusercontent.com/u/103068909/comments_on_github_2013.csv
For downloading discussions under the issues please take this dataset:
https://dl.dropboxusercontent.com/u/103068909/result_stargazers_2013_final_mature.csv
The .csv file must be located in the same directory where the python script is located.
Dig into my code for further reference..

Genesis of the dataset:

It was crawled from the Google Big Query

```
select payload_comment_commit_id, payload_comment_updated_at, payload_comment_created_at, 
payload_comment_path, payload_comment_user_id, payload_comment_user_avatar_url, 
payload_comment_user_url, payload_comment_user_login, payload_comment_user_gravatar_id, 
payload_comment_position, payload_comment_url, payload_comment_body, 
payload_comment_original_commit_id, payload_comment_original_position, repository_url
from [githubarchive:github.timeline]
where PARSE_UTC_USEC(payload_comment_created_at) >= PARSE_UTC_USEC('2012-11-01 00:00:00')
and PARSE_UTC_USEC(payload_comment_created_at) < PARSE_UTC_USEC('2013-11-01 00:00:00')
order by repository_url
```

**Expected result**

.JSON files, .TXT files (ready to be annotated by Brat), and .HTML files (i.e. with pull request content), finally - .LANG files with a prediction of langue used in a particular .TXT file

Third parties

We utilize GitHub API and HTML resources.
We use langid.py (https://github.com/saffsd/langid.py) to guess a language used in the dialogues.
We use the genderchecker.com portal to ask about the gender of a GitHub user, basing on the name (optionally provided by the person).

Requirements

Please check requirements.txt file for modules used in the program. Virtualenv compatible (won't require compiling external libraries etc.).

Other info

If using this dataset and/or tool, please give a reference url and mention (Oskar Jarczyk, 2014) in your paper
yet .bib citation info is not ready at this time

Acknowledgment

Name of this repository is a big Thank You and a tribute to my sister '**Linda**'
