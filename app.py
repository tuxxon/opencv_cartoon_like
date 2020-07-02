
import boto3
import botocore
import cv2
import cartoonizer
import hashlib
import json
import numpy
import os
import time


S3_URL = "https://{bucketName}.s3.ap-northeast-2.amazonaws.com/{keyName}"
DEST_S3_URL = "https://{bucketName}.s3.ap-northeast-2.amazonaws.com/{keyName}?t={timeStamp}"

kNORMALCARTOON = "normal-cartoon"

#
# ''' get the hash value for an image '''
#
def hash_image(img_path):

    f = open(img_path,'rb')
    d = f.read()
    f.close()
    h = hashlib.sha256(d).hexdigest()

    return h

#
#  Main handler of lambda_function
#
def lambda_handler(event, context):

    print("[DEBUG] event = {}".format(event))

    src_filename =event.get("name", None)
    filename_set = os.path.splitext(src_filename)
    basename = filename_set[0]
    ext = filename_set[1]
    h = basename.split("/")[1]

    #
    # local files
    #
    down_filename='/tmp/my_image{}'.format(ext)
    conv_filename='/tmp/normal_cartoon{}'.format(ext)
    down_jsonfile='/tmp/normal_cartoon.json'

    #
    # S3 files
    #
    s3_filename='public/{}/normal_cartoon{}'.format(h, ext)
    s3_paramfile='public/{}/normal_cartoon.json'.format(h) 

    if os.path.exists(down_filename):
        os.remove(down_filename)
    if os.path.exists(conv_filename):
        os.remove(conv_filename)
    if os.path.exists(down_jsonfile):
        os.remove(down_jsonfile)

    #
    # Download source image from S3.
    #
    s3 = boto3.client('s3')
    BUCKET_NAME = os.environ.get("BUCKET_NAME")
    S3_KEY = src_filename

    try:
        s3.download_file(BUCKET_NAME, S3_KEY, down_filename)        
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("===error message ===> {}".format(e))
            print("The object does not exist: s3://{}/{}".format(BUCKET_NAME, S3_KEY))
        else:
            raise

    image = cv2.imread(down_filename)
    output = cartoonizer.cartoonize(image)
    cv2.imwrite(conv_filename, output)

    #
    # Upload the converion image to S3
    #
    s3.upload_file(conv_filename, BUCKET_NAME, s3_filename)

    j = {}
    images = {
        "source" : S3_URL.format(
            bucketName = BUCKET_NAME, 
            keyName = src_filename
        ),
        "params" : j,
        "dest" : DEST_S3_URL.format(
            bucketName = BUCKET_NAME, 
            keyName = s3_filename,
            timeStamp = time.time()
        )        
    }

    return {
        "statusCode": 200,
        "body": {"images": images }
    }