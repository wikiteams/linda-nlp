for %%i in (pull*.txt) do python langid\langid.py -n -d < %%i > %%i.one.lang