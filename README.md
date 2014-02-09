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


**Usage description**

It's a command prompt program, requires Python 2.7+

```
python pullrequest.py client_oath_id client_secret
```

or unix nohup version

```
nohup python pullrequest.py client_oath_id client_secret > logs.txt &
```

Be advised, that GitHub quota mechanism may apply and cut you from downloading through urllib and API.

**Required data**

You will need to place a dataset .csv file which you can download from here: https://dl.dropboxusercontent.com/u/103068909/comments_on_github_2013.csv
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

.JSON files, .TXT files (ready to be annotated by Brat), and .HTML files (i.e. with pull request content)

Acknowledgment

Name of this repository is a big Thank You and a tribute to my sister '**Linda**'
