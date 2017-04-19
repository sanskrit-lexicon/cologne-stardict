dictList=(acc ae ap ap90 ben bhs bop bor bur cae ccs gra gst ieg inm krm mci md mw mw72 mwe pd pe pgn pui pw pwg sch shs skd snp stc vcp vei wil yat)
for DICT in "${dictList[@]}"
do
echo "downloading "$DICT"_xml.zip ..."
curl -o input/zips/"$DICT"_xml.zip http://s3.amazonaws.com/sanskrit-lexicon/blobs/"$DICT"_xml.zip
done

cd input/extracted
for DICT in "${dictList[@]}"
do
echo "unzipping "$DICT"_xml.zip ..."
unzip -o ../zips/"$DICT"_xml.zip
done

echo "Copying latest hwnorm1c.txt file."
echo "It presumes that the hwnorm1 repository is sibling of cologne-stardict repository."
cp ../hwnorm1/ejf/hwnorm1c/hwnorm1c.txt input/hwnorm1c.txt
