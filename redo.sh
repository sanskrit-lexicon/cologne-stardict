echo "Copying latest hwnorm1c.txt file."
echo "It presumes that the hwnorm1 repository is sibling of cologne-stardict repository."
cd ../hwnorm1
git pull origin master
cd ../cologne-stardict
cp ../hwnorm1/sanhw1/hwnorm1c.txt input/hwnorm1c.txt

dictList=(acc ae ap ap90 ben bhs bop bor bur cae ccs gra gst ieg inm krm mci md mw mw72 mwe pd pe pgn pui pw pwg sch shs skd snp stc vcp vei wil yat)
for Val in "${dictList[@]}"
do
	echo 'Started' $Val 'handling'.
	# python27 make_babylon.py input/extracted/pywork $Val $1
	python2 make_babylon.py input/extracted/pywork $Val $1
done
