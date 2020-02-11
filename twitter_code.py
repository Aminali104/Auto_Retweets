# This code retweets five latest tweets of a user with a comment 

import twitter, random, os, boto3
import logging
from base64 import b64decode

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def decrypt_credentials():
	# get the encrypted environment varialbes 
	ENCRYPTED_APP_KEY =os.environ['APP_KEY']
	ENCRYPTED_APP_SECRET = os.environ['APP_SECRET']
	ENCRYPTED_OAUTH_TOKEN = os.environ['OAUTH_TOKEN']
	ENCRYPTED_OAUTH_TOKEN_SECRET = os.environ['OAUTH_TOKEN_SECRET']
	
	decrypted_keys = {}
	# decryption of environment varialbes
	decrypted_keys['APP_KEY'] = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_APP_KEY))['Plaintext']
	decrypted_keys['APP_SECRET'] = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_APP_SECRET))['Plaintext']
	decrypted_keys['OAUTH_TOKEN'] = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_OAUTH_TOKEN))['Plaintext']
	decrypted_keys['OAUTH_TOKEN_SECRET'] = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_OAUTH_TOKEN_SECRET))['Plaintext']
	
	return decrypted_keys
	
	# function to retweet 
def retweet(decrypted_keys, event):
	
	list = ["""Check this out""", """This sounds interesting""", """RT"""]
	api = twitter.Api(decrypted_keys['APP_KEY'], decrypted_keys['APP_SECRET'], decrypted_keys['OAUTH_TOKEN'], decrypted_keys['OAUTH_TOKEN_SECRET'])
	# get the 5 latest tweets of the user
	statuses = api.GetUserTimeline(screen_name = event['name'])[:5]
	status_id = []
	
	# loop to ignore retweets of the user
	for i in range(len(statuses)):
		t = statuses[i].text[:2]
		if (t !='RT'):
			status_id.append(str(statuses[i].id))
	print status_id
	
	# loop to retweet with a comment from your account 
	for i in range(len(status_id)):
		retweet_url = """https://twitter.com/inserverless/status/""" + status_id[i]
		status = random.choice(list) + " " + retweet_url
		try:
			api.PostUpdate(status)
		# twitter throws an exception for duplicate tweets, hence the catch block
		except:
			print 'dulplicate post'
			continue

def lambda_handler(event, context):
	
	logger.debug('input:{}'.format(event))
	decrypted_keys = decrypt_credentials()
	retweet(decrypted_keys, event)
	
	logger.debug('output: {}'.format('Success'))
	return 'Success!'