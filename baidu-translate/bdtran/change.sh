for f in $(ls *.py)
do
    sed -i 's/^import BdTran/from bdtran import BdTran/g' $f
    sed -i 's/^import HeadersSource/from bdtran import HeadersSource/g' $f
    sed -i 's/^import GetSignature/from bdtran import GetSignature/g' $f
done

