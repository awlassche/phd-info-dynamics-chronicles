###
### INPUT PARAMS: change as you please!
###
dir_corpus_annotated='../corpus/corpus_230420/corpus_230420_annotated'
dir_corpus_corrected='../corpus/corpus_230420/corpus_230420_corrected'
run_when='230807'


###
### SETUP: does output dir exist? 
###
if [ -d "../output/primitives_${run_when}" ] 
then
    echo "Directory ${wdir} exists." 
else
    mkdir -p "../output/primitives_${run_when}"
    echo "Creating ${run_when} output dir in ../output/"
fi


###
### RUNNING
###

echo "Parsing corpus_annotated"
python xml_parsing.py \
    -d "${dir_corpus_annotated}" \
    -s 1 \
    -o "../output/primitives_${run_when}/primitives_annotated.ndjson"

echo "Parsing corpus_corrected"
python xml_parsing.py \
    -d "${dir_corpus_corrected}" \
    -s 1 \
    -o "../output/primitives_${run_when}/primitives_corrected.ndjson"

echo "Generating IDs"
python give_ids.py \
    -ap "../output/primitives_${run_when}/primitives_annotated.ndjson" \
    -cp "../output/primitives_${run_when}/primitives_corrected.ndjson"

echo "Cleaning date tags on corrected corpus"
python month_tag_resolutions.py \
    -i "../output/primitives_${run_when}/primitives_corrected.ndjson" \
    -o "../output/primitives_${run_when}/primitives_corrected_monthly.ndjson"

echo "Cleaning date tags on annotated corpus"
python month_tag_resolutions.py \
    -i "../output/primitives_${run_when}/primitives_annotated.ndjson" \
    -o "../output/primitives_${run_when}/primitives_annotated_monthly.ndjson"