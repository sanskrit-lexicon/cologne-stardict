echo "Update hwnorm1"
cd ../hwnorm1
git pull origin master

echo "Update csl-orig"
cd ../csl-orig
git pull origin master

cd ../cologne-stardict
cp ../hwnorm1/sanhw1/hwnorm1c.txt input/hwnorm1c.txt

dictList=(acc ae ap ap90 ben bhs bop bor bur cae ccs gra gst ieg inm krm mci md mw mw72 mwe pd pe pgn pui pw pwg sch shs skd snp stc vcp vei wil yat lan armh lrv)
for Val in "${dictList[@]}"
do
	echo 'Started' $Val 'handling'.
	python3 make_babylon.py $Val $1
	echo '' 
done
