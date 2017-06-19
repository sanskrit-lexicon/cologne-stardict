# Usage : sh copy_license.sh inputdirectory outputdirectory
# sh copy_license.sh ../Cologne_localcopy output
dictList=(acc ae ap ap90 ben bhs bop bor bur cae ccs gra gst ieg inm krm mci md mw mw72 mwe pd pe pgn pui pw pwg sch shs skd snp stc vcp vei wil yat)
for Val in "${dictList[@]}"
do
	cp ../Cologne_localcopy/$Val/"$Val"txt/"$Val"header.xml output/licenses/"$Val"_license.xml
	cp ../Cologne_localcopy/$Val/"$Val"txt/"$Val"header.xml production/licenses/"$Val"_license.xml
done
