codedate=`date "+%Y%m%d"`
symbolpath="./symbols/"
wget "http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download" --user-agent="Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36" -O ${symbolpath}nasdaq-list-${codedate}.csv
/usr/bin/python update_symbols.py ${symbolpath}nasdaq-list-${codedate}.csv
wget "http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download" --user-agent="Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36" -O ${symbolpath}nyse-list-${codedate}.csv
/usr/bin/python update_symbols.py ${symbolpath}nyse-list-${codedate}.csv
wget "http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=amex&render=download" --user-agent="Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36" -O ${symbolpath}amex-list-${codedate}.csv
/usr/bin/python update_symbols.py ${symbolpath}amex-list-${codedate}.csv
