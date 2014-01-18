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
python pullrequest.py
```

Be advised, that GitHub quota mechanism may apply and cut you from downloading through urllib and API.

**Required data**

You will need to place a dataset .csv file which you can download from here: https://dl.dropboxusercontent.com/u/103068909/comments_on_github_2013.csv

**Expected result**

.JSON files, .TXT files (ready to be annotated by Brat), and .HTML files (i.e. with pull request content)

Other

Name of this repository is a big Thank You and a tribute to my sister 'Linda'
