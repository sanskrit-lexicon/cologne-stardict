cd ../csl-orig
git pull origin master
cd ../csl-websanlexicon
git pull origin master
cd ../csl-pywork
git pull origin master
cd v02
bash redo_xampp_all.sh

cd ../../cologne-stardict
echo "Copying latest hwnorm1c.txt file."
echo "It presumes that the hwnorm1 repository is sibling of cologne-stardict repository."
cp ../hwnorm1/sanhw1/hwnorm1c.txt input/hwnorm1c.txt
