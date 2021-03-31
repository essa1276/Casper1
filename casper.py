#!/bin/bash
# CasPer! v1
# A full all-in-one Google AND Bing Dorker Search and Analyzer Script
# Author: Hood3dRob1n
# Blog: http://kaoticcreations.blogspot.com
#
# Requires CURL, LYNX, NMAP, FIMAP, and SQLMAP to fully work with all modules and plugins
# See README.txt file for full instructions and description of available options
# Download: http://inf0rm3r.webuda.com/scripts/BinGoo.zip
# Demo Video: LINK: http://www.youtube.com/watch?v=IILmJr_Xvyw
#             LINK2: http://www.youtube.com/watch?v=ikbHwNC2nuo

# Start the magic



# CONFIGURATION SECTION
#<= CHANGE BELOW THIS AS NEEDED =>
#Path to SQLMAP 
SPATH=/home/hood3drob1n/fun/sqlmap
#Path to FIMAP
FPATH=/home/hood3drob1n/fun/fimap/src
# Junk and Temp Files Location for tmp storage while script does its thing
JUNK=/tmp
# Pre-set for pagefinder plugin to use admin.lst file for finding admin files but can change to search for anything (plugins/pinfo.lst for example) based on server response and given word list with one per line, change as you like just make sure it exists before you run if you do :p
FINDERLIST=plugins/admin.lst
#<= CHANGE ABOVE THIS AS NEEDED =>



#VARIABLES
#G=Goole & B=Bing
METH=G
STORAGE1=$(mktemp -p "$JUNK" -t fooooobar1.tmp.XXX)
STORAGE2=$(mktemp -p "$JUNK" -t fooooobar2.tmp.XXX)
STORAGE3=$(mktemp -p "$JUNK" -t fooooobar3.tmp.XXX)
STORAGE4=$(mktemp -p "$JUNK" -t fooooobar4.tmp.XXX)
STORAGE5=$(mktemp -p "$JUNK" -t fooooobar5.tmp.XXX)
CHK1=$(mktemp -p "$JUNK" -t fooooochk1.tmp.XXX)
CHK2=$(mktemp -p "$JUNK" -t fooooochk2.tmp.XXX)
uagent1="Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00"
uagent2="Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20120427 Firefox/15.0a1"
uagent3="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6"
uagent4="Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0"
#1=Opera, 2=Chrome, 3=FireFox, 4=IE
trapper=0

#First a simple Bashtrap function to handle interupt (CTRL+C)
trap bashtrap INT

bashtrap(){
	if [ "$trapper" = 0 ]; then
		echo
		echo
		echo 'CTRL+C has been detected!.....shutting down now' | grep --color '.....shutting down now'
		rm -rf "$STORAGE1" 2> /dev/null
		rm -rf "$STORAGE2" 2> /dev/null
		cat "$STORAGE3" | uniq >> results/crash_dumped.results 2> /dev/null 2>&1
		rm -rf "$STORAGE3" 2> /dev/null
		rm -rf "$STORAGE4" 2> /dev/null
		rm -rf "$CHK1" 2> /dev/null
		rm -rf "$CHK2" 2> /dev/null
		rm -rf lnkfile-tmp_* 2> /dev/null
		#Kill any running instances in case we ran large file and spawned background processes...
		ps aux | grep "./bingoo" | cut -d' ' -f6 | while read selfkill
		do
			kill -9 "$selfkill" 2> /dev/null
		done
		#exit entire script if called
		exit 0
	fi
}
#End bashtrap()

# Choose Search Engine...
start_engine(){
echo
echo "Please select which option you would like to use: " | grep --color -E 'Please select which option you would like to use'
select search_engine in "Google" "Bing" "Bing Geo Dorker" "Bing Shared Hosting Check" "Digger Recon Tool" "Analyze & Tools"
do
	case $search_engine in
		"Google")
			METH=G
			core
			g_cleaner
		;;
		"Bing")
			METH=B
			core
			bing_cleaner
		;;
		"Bing Geo Dorker")
			bing_geo_dorker
		;;
		"Bing Shared Hosting Check")
			bing_shared_hosting_check
		;;
		"Digger Recon Tool")
			digger_recon
		;;
		"Analyze & Tools")
			analyze_type
		;;
		*)
			echo "There's only a few options dummy - You sir are a failure!"
			exit 0;
		;;
	esac
done
}

# Banner
banner(){
cat<<"EOT"
          -----------+--------------+------------+--
'---------------------By-Casper----'
EOT
}

gfinder_banner(){
cat << "EOT"
         _\|/_
         (o o)
 +----oOO-{_}-OOo----------------------------+
 |       Aku akan selalu mencintaimu
 --------------------------+
EOT
echo
}

# Bing Banner
bing_banner(){
cat << "EOT"
         _\|/_
         (o o)
 +----oOO-{_}-OOo-----+
 |  Bing! Dorker v1   |
 |  By: Casper   |
 +--------------------+
EOT
echo
}

# Usage
usage(){
	echo
	echo "USAGE: ./bingoo " | grep --color -E 'USAGE||bingoo'
	echo "Then just follow prompts..." | grep --color 'Then just follow prompts'
	echo
}

# Google Search
g_finder(){
# We use LYNX to query Google search engine. From Burp test the page count changes by 10 each time you change pages sp we make a nice while loop so that while less than 110 (or 11pages of results) continue checking for links and then increase page count by ten to get next set of results. We borrow some kick ass sed scripts to perform urldecoding of results to make it easier to read and interpret with human eye :)
	while [ "$COUNT" -le 250 ];
	do
		lynx "http://www.google.com/search?q=$1&start=$COUNT" -dump -listonly | grep 'url?q=' | cut -d ' ' -f4 | sed 's/http:\/\/www.google.com\/url?q=//' | sed 's/\(&sa=\).*//' | sed -f plugins/urldecode.sed >> "$STORAGE1"
		COUNT=$(( $COUNT +10 ))
	done
	echo
}

# clean results and place in safe storage file for user to walk away with and then print the results for them to see in terminal
g_cleaner(){
	cat "$STORAGE1" | sort | uniq > g-links.txt
	echo "Found $(wc -l g-links.txt | cut -d' ' -f1) Links:" | grep --color -E 'Found||Links'
	cat g-links.txt
	echo '' > "$STORAGE1"
	analyze_type
}

# Bing Search
bing_dorker(){
while [ "$COUNT" -le 225 ]; do
	lynx "http://www.bing.com/search?q=$DORK&qs=n&pq=$DORK&sc=8-5&sp=-1&sk=&first=$COUNT&FORM=PORE" -dump -listonly >> "$STORAGE1"
	COUNT=$((COUNT +12))
done
}

# Clean Bing results to usable format
bing_cleaner(){
	# Clean up results from any possible sites we dont care about or cause high amounts of false positives (add your site like this: 
	# grep -v 'site.com' (add pipe in front and after as needed) - maybe make black list variable in future to catch all...
	# dont forget the section at bottom of script as well if you make changes....
	cat "$STORAGE1" | grep -v 'http://www.bing.com' | grep -v 'javascript:void' | grep -v 'Hidden links:' | grep -v 'Visible links' | grep -v 'References' | grep -v 'msn.com' | grep -v 'microsoft.com' | grep -v 'yahoo.com' | grep -v 'live.com' | grep -v 'microsofttranslator.com' | grep -v 'irongeek.com' | grep -v 'hackforums.net' | grep -v 'freelancer.com' | grep -v 'facebook.com' | grep -v 'mozilla.org' | grep -v 'stackoverflow.com' | grep -v 'php.net' | grep -v 'wikipedia.org' | grep -v 'amazon.com' | grep -v '4shared.com' | grep -v 'wordpress.org' | grep -v 'about.com' | grep -v 'phpbuilder.com' | grep -v 'phpnuke.org' | grep -v 'youtube.com' | grep -v 'p4kurd.com' | grep -v 'tizag.com' | grep -v 'devshed.com' | grep -v 'owasp.org' | grep -v 'fictionbook.org' | grep -v 'silenthacker.do.am' | grep -v 'codingforums.com' | grep -v 'tudosobrehacker.com' | grep -v 'zymic.com' | grep -v 'gaza-hacker.com' | grep -v 'immortaltechnique.co.uk' | cut -d' ' -f4 | sed -f plugins/urldecode.sed | sed '/^$/d' | sed 's/9.//' | sed '/^$/d' | sort | uniq > b-links.txt
	echo
	echo "Found $(wc -l b-links.txt | cut -d' ' -f1) Unique Links in total:" | grep --color -E 'Found||Unique Links in total'
	cat b-links.txt
	echo '' > "$STORAGE1"
	analyze_type
}

# Core of search tools
core(){
	echo
	if [ $METH == G ]; then
		COUNT=10
	fi
	if [ $METH == B ]; then
		bing_banner
		COUNT=9
	fi
	echo "Do you want to run single dork scan or import list of dorks to scan with?" | grep --color 'Do you want to run single dork scan or import list of dorks to scan with'
	select scan_type in "Single Dork Scan" "Mass Scan w/Imported Dork List" "Exit"
	do
		case $scan_type in
			"Single Dork Scan")
				echo
				echo "Please provide Google dork to use: " | grep --color 'Please provide Google dork to use'
				read DORK
				echo
				echo "Starting scan, be patient this will take a sec..." | grep --color -E 'Starting scan||be patient this will take a sec'
				echo
				if [ "$METH" == G ]; then
					g_finder "$DORK"
					g_cleaner
				fi
				if [ "$METH" == B ]; then
					bing_dorker "$DORK"
					bing_cleaner
				fi
				gfinder_banner
				start_engine
			;;
			"Mass Scan w/Imported Dork List")
				echo
				echo "OK, please provide path to dork file: " | grep --color -E 'OK||please provide path to dork file'
				read DORKFILE
				echo
				if [ ! -r "$DORKFILE" ]; then
					echo "Can't read provided file, please try another file or check permissions..." | grep --color -E 'Can||t read provided file||please try another file or check permissions'
					echo			
				else
					echo "Starting scan, be patient this will take a sec..." | grep --color -E 'Starting scan||be patient this will take a sec'
					echo
					if [ $METH == B ]; then
						cat "$DORKFILE" | while read dork
						do
							while [ "$COUNT" -le 225 ]; do
								lynx "http://www.bing.com/search?q=$dork&qs=n&pq=$dork&sc=8-5&sp=-1&sk=&first=$COUNT&FORM=PORE" -dump -listonly >> "$STORAGE1"
								COUNT=$((COUNT +12))
							done
							echo "Found $(wc -l $STORAGE1 | cut -d' ' -f1) Links..." | grep --color -E 'Found||Links'
							COUNT=9
						done
						bing_cleaner
					fi
					if [ $METH == G ]; then
						cat "$DORKFILE" | while read dork
						do
							g_finder "$dork"
							echo "Found $(wc -l $STORAGE1 | cut -d' ' -f1) Links..." | grep --color -E 'Found||Links'
							COUNT=10
						done
						g_cleaner
					fi
				fi
				gfinder_banner
				start_engine
			;;
			"Exit")
				echo
				echo "OK, exiting now...." | grep --color -E 'OK||exiting now'
				echo
				exit 0
			;;
		esac
	done
}

# Combine Bing and Google search results into single file to make easier to work with
biglinks_funk(){
	cat b-links.txt > "$STORAGE2"
	cat g-links.txt >> "$STORAGE2"
	cat "$STORAGE2" | sort | uniq > biglinks.txt 2> /dev/null
}

# Print proper message for found LFI/RFI injections (based on regex)
lfi_reg(){
	echo "[ LFI VULN FOUND ] $sitetargets2" | grep --color "\[ LFI VULN FOUND \]"
	echo "      REGEX => $CHKREG" | grep --color "REGEX =>"
	echo "[ LFI VULN FOUND ] $sitetargets2
      REGEX => $CHKREG" >> "$STORAGE3" 2> /dev/null
	FAIL=1
}

# Print proper message for found SQL injections (based on regex)
sqli_reg(){
	echo "[ SQL VULN FOUND ] $sitetargets2" | grep --color "\[ SQL VULN FOUND \]"
	echo "      REGEX => $CHKREG" | grep --color "REGEX =>"
	echo "[ SQL VULN FOUND ] $sitetargets2
      REGEX => $CHKREG" >> "$STORAGE3" 2> /dev/null
	FAIL=1
}

# Compare results output returned after insertion of "'" and if more than 15% variance then check for missing tables rows (common sign of SQLi flaw) 
statistic_count(){
		#Check byte count for each page we checked with curl (pre and post injection)
		CHKCOUNT1=$(wc -l "$CHK1" | cut -d' ' -f1)
		CHKCOUNT2=$(wc -l "$CHK2" | cut -d' ' -f1)
		CHKCOUNTA=$(cat "$CHK1" | grep '<tr>' | wc -l)
		CHKCOUNTB=$(cat "$CHK2" | grep '<tr>' | wc -l)
		#Find out how much was lost
		qq=$(expr $CHKCOUNT1 - $CHKCOUNT2)
		#FInd out what percentage of original that missing chunk is
		rr=$(echo "scale=2; $qq / $CHKCOUNT1" | bc -l 2> /dev/null)
		#Get it from decimal back to usable numbers since were using bash to do everything :p
		zz=$(echo $rr | sed 's/.//')
		#Check for variance. Anything less than check number means it is missing some serious text from the injection and should be worth investigating further manually
		if [ "$zz" != 0 ]; then
			if [ "$zz" \< 16 ]; then
				if [ "$CHKCOUNTA" != "$CHKCOUNTB" ]; then
					echo "[ POSSIBLE BLIND ] $sitetargets" | grep --color '\[ POSSIBLE BLIND \]'
					echo "[ POSSIBLE BLIND ] $sitetargets" >> "$STORAGE3" 2> /dev/null
					FAIL=1
				fi			

			fi
		fi
}

# Check for possible injection vulnerabilities based upon simple regex technique
regex_check(){
#Set SQLi Regex Array Values and keep it easy to add new ones to the list
SQLiREGEX[0]="Warning: mysql_query()";
SQLiREGEX[1]="Warning: mysql_fetch_row()";
SQLiREGEX[2]="Warning: mysql_fetch_assoc()";
SQLiREGEX[3]="Warning: mysql_fetch_object()";
SQLiREGEX[4]="Warning: mysql_numrows()";
SQLiREGEX[5]="Warning: mysql_num_rows()";
SQLiREGEX[6]="Warning: mysql_fetch_array()";
SQLiREGEX[7]="Warning: pg_connect()";
SQLiREGEX[8]="Supplied argument is not a valid PostgreSQL result";
SQLiREGEX[9]="PostgreSQL query failed: ERROR: parser: parse error";
SQLiREGEX[10]="MySQL Error";
SQLiREGEX[10]="MySQL ODBC";
SQLiREGEX[11]="MySQL Driver";
SQLiREGEX[12]="supplied argument is not a valid MySQL result resource";
SQLiREGEX[13]="on MySQL result index";
SQLiREGEX[14]="Oracle ODBC";
SQLiREGEX[15]="Oracle Error";
SQLiREGEX[16]="Oracle Driver";
SQLiREGEX[17]="Oracle DB2";
SQLiREGEX[18]="Microsoft JET Database Engine error";
SQLiREGEX[19]="ADODB.Command";
SQLiREGEX[20]="ADODB.Field error";
SQLiREGEX[21]="Microsoft Access Driver";
SQLiREGEX[22]="Microsoft VBScript runtime error";
SQLiREGEX[23]="Microsoft VBScript compilation error";
SQLiREGEX[24]="Microsoft OLE DB Provider for SQL Server error";
SQLiREGEX[25]="OLE/DB provider returned message";
SQLiREGEX[26]="OLE DB Provider for ODBC";
SQLiREGEX[27]="ODBC SQL";
SQLiREGEX[28]="ODBC DB2";
SQLiREGEX[29]="ODBC Driver";
SQLiREGEX[30]="ODBC Error";
SQLiREGEX[31]="ODBC Microsoft Access";
SQLiREGEX[32]="ODBC Oracle";
SQLiREGEX[33]="JDBC SQL";
SQLiREGEX[34]="JDBC Oracle";
SQLiREGEX[35]="JDBC MySQL";
SQLiREGEX[36]="JDBC error";
SQLiREGEX[37]="JDBC Driver";
SQLiREGEX[38]="Invision Power Board Database Error";
SQLiREGEX[39]="DB2 ODBC";
SQLiREGEX[40]="DB2 error";
SQLiREGEX[41]="DB2 Driver";
SQLiREGEX[42]="error in your SQL syntax";
SQLiREGEX[43]="unexpected end of SQL command";
SQLiREGEX[44]="invalid query";
SQLiREGEX[45]="SQL command not properly ended";
SQLiREGEX[46]="Error converting data type varchar to numeric";
SQLiREGEX[47]="An illegal character has been found in the statement";
SQLiREGEX[48]="Active Server Pages error";
SQLiREGEX[49]="ASP.NET_SessionId";
SQLiREGEX[50]="ASP.NET is configured to show verbose error messages";
SQLiREGEX[51]="A syntax error has occurred";
SQLiREGEX[52]="ORA-01756";
SQLiREGEX[53]="Error Executing Database Query";
SQLiREGEX[54]="Unclosed quotation mark";
SQLiREGEX[55]="BOF or EOF";
SQLiREGEX[56]="GetArray()";
SQLiREGEX[57]="FetchRow()";
SQLiREGEX[58]="Input string was not in a correct format";
SQLiREGEX[59]="Warning: include(":
SQLiREGEX[60]="Warning: require_once(";
SQLiREGEX[61]="function.include";
SQLiREGEX[62]="Disallowed Parent Path";
SQLiREGEX[63]="function.require";
SQLiREGEX[64]="Warning: main(";
SQLiREGEX[65]="Warning: session_start()";
SQLiREGEX[66]="Warning: getimagesize()";
SQLiREGEX[67]="Warning: mysql_result()";
SQLiREGEX[68]="Warning: pg_exec()";
SQLiREGEX[69]="Warning: array_merge()";
SQLiREGEX[70]="Warning: preg_match()";
SQLiREGEX[71]="Incorrect syntax near";
SQLiREGEX[72]="ORA-00921: unexpected end of SQL command";
SQLiREGEX[73]="Warning: ociexecute()";
SQLiREGEX[74]="Warning: ocifetchstatement()";
SQLiREGEX[75]="error ORA-";

#Run Regex check on returned page for common indications of vulnarability (blatant error messages basically)
	z=0
	i=1
	while [ "$z" -lt ${#SQLiREGEX[@]} ];
	do
		FAIL=1
		CHKREG=${SQLiREGEX[$i-1]}
		grep -i "$CHKREG" "$CHK2" 2> /dev/null 2>&1
		if [ "$?" == 0 ]; then
		#Add to Case statement if you add new LFI regex to the regex array to help sort results better :)
			case "$CHKREG" in
				"Warning: include(")
					lfi_reg
				;;
				"Warning: require_once(")
					lfi_reg
				;;
				"function.include")
					lfi_reg
				;;
				"Disallowed Parent Path")
					lfi_reg
				;;
				"include_path")
					lfi_reg
				;;
				"function.require")
					lfi_reg
				;;
				"Warning: main(")
					lfi_reg
				;;
				*)
					sqli_reg
				;;
			esac
		else
			FAIL=0
		fi
		z=$(( z +1 ))
		i=$(( i +1 ))
	done
	if [ "$FAIL" == 0 ]; then
		statistic_count			
	fi
	if [ "$FAIL" == 0 ]; then
		echo "Nothing Found: $sitetargets"			
	fi
	cat "$STORAGE3" | uniq >> "$STORAGE5" 2> /dev/null 2>&1
}

# Break out the curl magic so we can call this function and launch in background to help speed things up when we have large list files
curl_magic(){
	cat "$lnkfile" | while read sitetargets
	do
		sitetargets2=$(echo "$sitetargets" | sed 's/$/%27/');
		curl "$sitetargets" --ssl --retry 1 --retry-delay 3 --connect-timeout 2 --no-keepalive -s -e "http://www.google.com/q?=foobar" -A "$uagent1" -o "$CHK1"
		curl "$sitetargets2" --ssl --retry 1 --retry-delay 3 --connect-timeout 2 --no-keepalive -s -e "http://www.google.com/q?=foobar" -A "$uagent2" -o "$CHK2"
		regex_check 2> /dev/null
	done
}

# COre of Injection Analysis Tool Section
injector_tester_core(){
	if [ "$SOURCELINKS" == 1 ]; then
		LINKFILE=b-links.txt
	fi
	if [ "$SOURCELINKS" == 2 ]; then
		LINKFILE=g-links.txt
	fi
	if [ "$SOURCELINKS" == 3 ]; then
		biglinks_funk
		LINKFILE=biglinks.txt
	fi
	if [ "$SOURCELINKS" == 4 ]; then
		LINKFILE="$USERLINKS"
	fi
	if [ "$SOURCELINKS" == 5 ]; then
		LINKFILE=shared.txt
	fi
	if [ "$SOURCELINKS" == 6 ]; then
		LINKFILE=GEO.txt
	fi
	echo
	if [ ! -r "$LINKFILE" ]; then
		echo "Can't read link file, please make sure file exists and try again!" | grep --color -E 'Can||t read link file||please make sure file exists and try again'
		analyze_type
	fi
	LINKFILECOUNT=$(wc -l $LINKFILE | cut -d' ' -f1)

# Perform make shift multi-threading for link files larger than 2000 links as otherwise it might take a while to run through all and run all checks
	if [ "$LINKFILECOUNT" -ge 2000 ]; then
		#Split  LINKFILE into smaller chunks for faster processing time (more noticable when using mass dorker and have more than 2000 links to analyze)
		split -d -l 1000 "$LINKFILE" lnkfile-tmp_
		echo "Analyzing $LINKFILECOUNT links, this may take a while since you have a large number of links to test...." | grep --color -E 'Analyzing||links||this may take a while since you have a large number of links to test'
		for lnkfile in $(find . -type f -name lnkfile-tmp_\* 2> /dev/null);
		do
			curl_magic &
			
		done
		# Wait for background processes to finish before printing any results...
		wait
		cat "$STORAGE5" | grep -v 'REGEX' | grep --color -E '\[ SQL VULN FOUND \] || \[ LFI VULN FOUND \] || REGEX' | sort | uniq > results/bingoo_tmp.results
		echo
		cat results/bingoo_tmp.results | grep '\[ SQL VULN FOUND \]' >> results/SQLi.results 2> /dev/null 2>&1
		cat results/bingoo_tmp.results | grep '\[ LFI VULN FOUND \]' >> results/LFI.results 2> /dev/null 2>&1
		cat results/bingoo_tmp.results | grep '\[ POSSIBLE BLIND \]' >> results/possibles.results 2> /dev/null 2>&1
		sqlicount=$(wc -l results/SQLi.results | cut -d' ' -f1)
		lficount=$(wc -l results/LFI.results | cut -d' ' -f1)
		possibles=$(wc -l results/possibles.results | cut -d' ' -f1)
		echo
		echo "RESULTS POST ANALYSIS: " | grep --color 'RESULTS POST ANALYSIS'
		echo "SQLi Found Links: $sqlicount" | grep --color 'SQLi Found Links'
		echo "LFI Found Links: $sqlicount" | grep --color 'LFI Found Links'
		echo "Blind Possibles Links: $sqlicount" | grep --color 'Blind Possibles Links'
		echo
		echo "Check the results files for more details..."
		echo
		rm -rf lnkfile-tmp_* 2> /dev/null
		rm -f results/bingoo_tmp.results 2> /dev/null
		if [ "$SHARE" != 1 ]; then
			banner | grep --color -E 'By||Hood3dRob1n'
			analyze_type
		fi
	fi

# If under 2000 links then process aa little different
	if [ "$LINKFILECOUNT" -lt 2000 ]; then
		#Split LINKFILE into smaller chunks for faster processing time (more noticable when using mass dorker and have more than 2000 links to analyze)
		split -d -l 500 "$LINKFILE" lnkfile-tmp_
		echo "Analyzing $LINKFILECOUNT links, this may take a few...." | grep --color -E 'Analyzing||links||this may take a few'
		for lnkfile in $(find . -type f -name lnkfile-tmp_\* 2> /dev/null);
		do
			curl_magic &
			
		done
# Wait for background processes to finish before printing any results...
		wait
		cat "$STORAGE5" | grep -v 'REGEX' | grep --color -E '\[ SQL VULN FOUND \] || \[ LFI VULN FOUND \] || REGEX' | sort | uniq > results/bingoo_tmp.results
		echo
		cat results/bingoo_tmp.results | grep '\[ SQL VULN FOUND \]' >> results/SQLi.results 2> /dev/null 2>&1
		cat results/bingoo_tmp.results | grep '\[ LFI VULN FOUND \]' >> results/LFI.results 2> /dev/null 2>&1
		cat results/bingoo_tmp.results | grep '\[ POSSIBLE BLIND \]' >> results/possibles.results 2> /dev/null 2>&1
		sqlicount=$(wc -l results/SQLi.results | cut -d' ' -f1)
		lficount=$(wc -l results/LFI.results | cut -d' ' -f1)
		possibles=$(wc -l results/possibles.results | cut -d' ' -f1)
		echo
		echo "RESULTS POST ANALYSIS: " | grep --color 'RESULTS POST ANALYSIS'
		echo "SQLi Found Links: $sqlicount" | grep --color 'SQLi Found Links'
		echo "LFI Found Links: $sqlicount" | grep --color 'LFI Found Links'
		echo "Blind Possibles Links: $sqlicount" | grep --color 'Blind Possibles Links'
		echo
		echo "Check the results files for more details..."
		echo
		rm -rf lnkfile-tmp_* 2> /dev/null
		rm -f results/bingoo_tmp.results 2> /dev/null
		if [ "$SHARE" != 1 ]; then
			banner | grep --color -E 'By||Hood3dRob1n'
			analyze_type
		fi
	fi
}

analyze_type(){
	echo
	echo "Please select which links file to analyze or what tool to use: " | grep --color 'Please select which links file to analyze or what tool to use'
	select links_files in "Bing Links File: b-links.txt" "Google Links File: g-links.txt" "Both Bing & Google Links Files" "My Links File" "Admin Page Finder" "LFI Tools" "SQLi Tools" "Return to Dorker" "Exit"
	do
		case $links_files in
			"Bing Links File: b-links.txt")
				echo
				SOURCELINKS=1
				SHARE=0
				injector_tester_core
			;;
			"Google Links File: g-links.txt")
				echo
				SOURCELINKS=2
				SHARE=0
				injector_tester_core
			;;
			"Both Bing & Google Links Files")
				echo
				SOURCELINKS=3
				SHARE=0
				injector_tester_core
			;;
			"My Links File")
				echo
				echo "OK, please provide path to links file: " | grep --color -E 'OK||please provide path to links file'
				read USERLINKS
				echo
				if [ ! -r "$USERLINKS" ]; then
					echo "Can't read provided file, please try another file or check permissions..." | grep --color -E 'Can||t read provided file||please try another file or check permissions'
					echo
					analyze_type
				else
					SOURCELINKS=4
					SHARE=0
					echo
					injector_tester_core
				fi
			;;
			"Admin Page Finder")
				source plugins/pagefinder
			;;
			"LFI Tools")
				bingoo_lfi_tools
			;;
			"SQLi Tools")
				bingoo_sqli_tools
			;;
			"Return to Dorker")
				banner | grep --color -E 'By||Hood3dRob1n'
				start_engine
			;;
			"Exit")
				echo
				echo "OK, exiting now..." | grep --color -E 'OK||exiting now'
				echo
				exit 0;
			;;
		esac
	done
}


#Confirm DNS tool of choice for resolving and use accordingly with Bing Shared Hosting Checker
dns_chk(){
command -v resolveip >/dev/null 2>&1 || { echo >&2 "Resolveip isn't installed! Checking for alternative methods to resolve hostnames..." | grep --color -E 'Resolveip isn||t installed||Checking for alternative methods to resolve hostnames'; dns_chk1; }
resolver=1
}
dns_chk1(){
command -v dig >/dev/null 2>&1 || { echo >&2 "Dig isn't installed either! Checking for one more alternative method to resolve hostnames..." | grep --color -E 'Dig isn||t installed either||Checking for one more alternative method to resolve hostnames'; dns_chk2; }
resolver=2
}
dns_chk2(){
command -v host >/dev/null 2>&1 || { echo >&2 "Host tool isn't installed either! Checking for nslookup as last hope..." | grep --color -E 'Host tool isn||t installed either||Checking for nslookup as last hope'; dns_chk3; }
resolver=3
}
dns_chk3(){
command -v nslookup >/dev/null 2>&1 || { echo >&2 "nslookup tool isn't installed either! Can't run script without ability to resolve IPs..." | grep --color -E 'nslookup tool isn||t installed either||Can||t run this option without ability to resolve to IPs'; start_engine; }
resolver=4
}

#Specific Bing module to run preset list of dorks at an IP to check for vulns on shared hosting sites to find an in :)
bing_shared_hosting_check(){
	bing_banner
	echo
	echo "Please provide site name or IP address to run check against: " | grep --color 'Please provide site name or IP address to run check against'
	read SHAREDTARGET
	echo
	dns_chk
	# Resolve hostname to ip so can run proper Bing Shared hosting check...
	# $SHAREDTARGET=hostname
	# $SHAREDTARGETIP=IP
	if [ `echo "$SHAREDTARGET" | egrep  "(([0-9]+\.){3}[0-9]+)|\[[a-f0-9:]+\]"`  ]; then
		SHAREDTARGETIP="$SHAREDTARGET"
		echo "OK, running check now..." | grep --color -E 'OK||running check now'
		echo
	else
		if [ "$resolver" == 1 ]; then
			SHAREDTARGETIP=`resolveip -s "$SHAREDTARGET"`
		fi
		if [ "$resolver" == 2 ]; then
			SHAREDTARGETIP=`dig +short "$SHAREDTARGET"`
		fi
		if [ "$resolver" == 3 ]; then
			SHAREDTARGETIP=`host "$SHAREDTARGET" | awk '/^[[:alnum:].-]+ has address/ { print $4 }'`
		fi
		if [ "$resolver" == 4 ]; then
			SHAREDTARGETIP=`nslookup "$SHAREDTARGET" | awk '/^Address: / { print $2 }'`
		fi
		if [ "$?" != 0 ]; then
		 	echo "Error: cannot resolve provided hostname $TARGET to known IP address" | grep --color -E 'Error||cannot resolve provided hostname||to known IP address'
			start_engine;
		fi
		echo 
		echo "OK, resolved $SHAREDTARGET to IP $SHAREDTARGETIP, running Bing dork tool now..." | grep --color -E 'OK||resolved||to IP||running Bing dork tool now'
	fi

	COUNT=9
	cat "dorks/sharedhosting.lst" | while read dork
	do
		while [ "$COUNT" -le 225 ]; do
			lynx "http://www.bing.com/search?q=ip%3a$SHAREDTARGETIP+$dork&qs=n&pq=ip%3a$SHAREDTARGETIP+$dork&sc=8-5&sp=-1&sk=&first=$COUNT&FORM=PORE" -dump -listonly >> "$STORAGE4"
			COUNT=$((COUNT +12))
		done
		echo "Found $(wc -l $STORAGE4 | cut -d' ' -f1) Links..." | grep --color -E 'Found||Links'
		COUNT=9
	done
	# Clean up results from any possible sites we dont care about or cause high amounts of false positives (add your site like this: 
	# grep -v 'site.com' (add pipe in front and after as needed) - maybe make black list variable in future to catch all...
	cat "$STORAGE4" | grep -v 'http://www.bing.com' | grep -v 'javascript:void' | grep -v 'Hidden links:' | grep -v 'Visible links' | grep -v 'References' | grep -v 'msn.com' | grep -v 'microsoft.com' | grep -v 'yahoo.com' | grep -v 'live.com' | grep -v 'microsofttranslator.com' | grep -v 'irongeek.com' | grep -v 'hackforums.net' | grep -v 'freelancer.com' | grep -v 'facebook.com' | grep -v 'mozilla.org' | grep -v 'stackoverflow.com' | grep -v 'php.net' | grep -v 'wikipedia.org' | grep -v 'amazon.com' | grep -v '4shared.com' | grep -v 'wordpress.org' | grep -v 'sourceforge.net' | grep -v 'about.com' | grep -v 'phpbuilder.com' | grep -v 'phpnuke.org' | grep -v 'youtube.com' | grep -v 'tizag.com' | grep -v 'devshed.com' | grep -v 'owasp.org' | grep -v 'fictionbook.org' | grep -v 'p4kurd.com' | grep -v 'silenthacker.do.am' | grep -v 'codingforums.com' | grep -v 'zymic.com' | grep -v 'gaza-hacker.com' | grep -v 'tudosobrehacker.com' | grep -v 'immortaltechnique.co.uk' | cut -d' ' -f4 | sed -f plugins/urldecode.sed | sed '/^$/d' | sed 's/9.//' | sed '/^$/d' | sort | uniq > shared.txt
	echo
	echo "Found $(wc -l shared.txt | cut -d' ' -f1) Unique Links in total:" | grep --color -E 'Found||Unique Links in total'
	rm -rf "$STORAGE4"
	SOURCELINKS=5
	SHARE=1
	echo
	injector_tester_core
	cat "$STORAGE5" > results/shared-hosting.results
	sharedcnt=$(cat results/shared-hosting.results | grep -v 'REGEX' | wc -l | cut -d' ' -f1)
	echo
	echo "Found $sharedcnt possibles, please check results/shared-hosting.results file for full details if you missed in terminal..." | grep --color -E 'Found||possibles||please check results||shared||hosting||results file for full details if you missed in terminal'
	echo
	rm -f shared.txt
	banner | grep --color -E 'By||Hood3dRob1n'
	start_engine
}


bing_geo_dorker(){
	bing_banner
	echo
	echo "Welcome to Geo Dorker" | grep --color "Welcome to Geo Dorker"
	echo
	echo "Give ONE site type or country code like one of the examples below and script will run dork using sites.lst and your choice as base..." | grep --color -E 'Give ONE site type or country code like one of the examples below and script will run dork using sites||lst and your choice as base'
	echo "Examples: " | grep --color "Examples"
	echo "http://www.thrall.org/domains.htm

AC AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BM BN BO BR BS BT BW BY BZ
CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CX CY CZ DE DJ DK DM DO DZ EC EE EG ER ES ET EU FI FJ FK FM FO FR
GA GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP  
KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ  
NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW
SA SB SC SD SE SG SH SI SK SL SM SN SO SR SS ST SV SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ
UA UG UK US UY UZ VA VC VE VG VI VN VU WF WS YE ZA ZM ZW 

BIZ COM INFO NET ORG AERO ASIA CAT COOP EDU GOV INT JOBS MIL MOBI MUSEUM TEL TRAVEL XXX"
	echo
	echo "NOTE: I dont do any checks so use something valid or you wont get results!" | grep --color 'NOTE:'
	echo
	echo "Please provide SITE TYPE or COUNTRY CODE to run check against: " | grep --color 'Please provide SITE TYPE or COUNTRY CODE to run check against'
	read BINGGEOCODE
	echo

	COUNT=9
	cat "dorks/site.lst" | sed "s/site:/site:$BINGGEOCODE/" | while read dork
	do
		while [ "$COUNT" -le 225 ]; do
			lynx "http://www.bing.com/search?q=$dork&qs=n&pq=$dork&sc=8-5&sp=-1&sk=&first=$COUNT&FORM=PORE" -dump -listonly >> "$STORAGE4"
			COUNT=$((COUNT +12))
		done
		echo "Found $(wc -l $STORAGE4 | cut -d' ' -f1) Links..." | grep --color -E 'Found||Links'
		COUNT=9
	done
	# Clean up results from any possible sites we dont care about or cause high amounts of false positives (add your site like this: 
	# grep -v 'site.com' (add pipe in front and after as needed) - maybe make black list variable in future to catch all in one spot for easier updates...
	cat "$STORAGE4" | grep -v 'http://www.bing.com' | grep -v 'javascript:void' | grep -v 'Hidden links:' | grep -v 'Visible links' | grep -v 'References' | grep -v 'msn.com' | grep -v 'microsoft.com' | grep -v 'yahoo.com' | grep -v 'live.com' | grep -v 'microsofttranslator.com' | grep -v 'irongeek.com' | grep -v 'hackforums.net' | grep -v 'freelancer.com' | grep -v 'facebook.com' | grep -v 'mozilla.org' | grep -v 'stackoverflow.com' | grep -v 'php.net' | grep -v 'wikipedia.org' | grep -v 'amazon.com' | grep -v '4shared.com' | grep -v 'wordpress.org' | grep -v 'sourceforge.net' | grep -v 'about.com' | grep -v 'phpbuilder.com' | grep -v 'phpnuke.org' | grep -v 'youtube.com' | grep -v 'tizag.com' | grep -v 'devshed.com' | grep -v 'owasp.org' | grep -v 'fictionbook.org' | grep -v 'p4kurd.com' | grep -v 'silenthacker.do.am' | grep -v 'codingforums.com' | grep -v 'zymic.com' | grep -v 'gaza-hacker.com' | grep -v 'tudosobrehacker.com' | grep -v 'immortaltechnique.co.uk' | cut -d' ' -f4 | sed -f plugins/urldecode.sed | sed '/^$/d' | sed 's/9.//' | sed '/^$/d' | sort | uniq > GEO.txt
	echo
	echo "Found $(wc -l GEO.txt | cut -d' ' -f1) Unique Links in total:" | grep --color -E 'Found||Unique Links in total'
	rm -rf "$STORAGE4"
	SOURCELINKS=6
	SHARE=1
	echo
	injector_tester_core
	cat "$STORAGE5" > results/"$BINGGEOCODE".results
	sharedcnt=$(cat results/"$BINGGEOCODE".results | grep -v 'REGEX' | wc -l | cut -d' ' -f1)
	echo
	echo "Found $sharedcnt possibles, please check results/$BINGGEOCODE.results file for full details if you missed in terminal..." | grep --color -E 'Found||possibles||please check results||$BINGGEOCODE||results file for full details if you missed in terminal'
	echo
	rm -f GEO.txt
	banner | grep --color -E 'By||Hood3dRob1n'
	start_engine
}


digger_recon(){
	dns_chk
	#IF it fails consider using EXPORT for exporting values from resolver....
	source plugins/digger
	wait
	banner | grep --color -E 'By||Hood3dRob1n'
	start_engine
}

bingoo_sqli_tools(){
	source plugins/SQLi
	wait
	banner | grep --color -E 'By||Hood3dRob1n'
	start_engine
}

bingoo_lfi_tools(){
	source plugins/LFI
	wait
	banner | grep --color -E 'By||Hood3dRob1n'
	start_engine
}

# MAIN FUNCTION CALLS
clear
banner | grep --color -E 'By||Hood3dRob1n'

# Check that user has LYNX installed already as its core of script
command -v lynx >/dev/null 2>&1 || { echo >&2 "LYNX isn't installed!  Can't use this tool without it..." | grep --color -E 'LYNX isn||t installed||Can||t use this tool without it'; exit 0; }
command -v curl >/dev/null 2>&1 || { echo >&2 "CURL isn't installed!  Can't use this tool without it..." | grep --color -E 'CURL isn||t installed||Can||t use this tool without it'; exit 0; }

# Check arguments passed to provide usage info for dummies
if [ "$1" == '-h' ] || [ "$1" == '--help' ]; then
	usage
	exit 0;
fi

start_engine


#remove our temp storage
rm -rf "$STORAGE1" 2> /dev/null
rm -rf "$STORAGE2" 2> /dev/null
rm -rf "$STORAGE3" 2> /dev/null
rm -rf "$CHK1" 2> /dev/null
rm -rf "$CHK2" 2> /dev/null

# bid farewell...
echo
echo "Hope you found what you were looking for. Until next time, Enjoy!" | grep --color -E 'Hope you found what you were looking for. Until next time||Enjoy'
echo
rm -rf lnkfile-tmp_* 2> /dev/null
# Greetz to and from INTRA!
#EOF