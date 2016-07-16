
for f in *.PDF
do
    ./pdf_to_csv.py $f $f".csv"
    ./splice_history_files.py "history.csv" $f".csv" "history.csv"
done
