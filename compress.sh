ZIPFILE=normal_cartoon_allinone.zip
zip -d $ZIPFILE app.py
zip -g $ZIPFILE app.py
zip -d $ZIPFILE cartoonizer.py
zip -g $ZIPFILE cartoonizer.py

#unzip cv2-python37.zip 
#cp app.py python/lib/python3.7/site-packages/
#cd python/lib/python3.7/site-packages/
#zip -r9 ../../../../$ZIPFILE .
#cd -
