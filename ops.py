import requests
try: import simplejson as json
except ImportError: import json

import pprint

OPS_REST_VERSION = '2.6.2'
NUMBER_SERVICE_STATUS = {
	'BRE001': 'Number Standardization Stopped',
	'BRE002': 'Number Standardization Stopped - Routed to Post Processing',
	'BRE003': 'RawId not Defined',
	'BRE004': 'Country Code not Valid',
	'BRE006': 'No Matching Pattern Found',
	'BRE007': 'Failed to convert sequence number for document',
	'BRE008': 'Illegal Country Code WO for APP-PRI',
	'BRE009': 'Invalid Sequence Number in KindCodeSet',
	'BRE010': 'Invalid Sequence Number in GenerateTargetId',
	'BRE011': 'Invalid Length for SN',
	'BRE012': 'SN Length Over Max Size',
	'BRE013': 'Kind Code not valid for this Time Period',
	'BRE014': 'Attempt to Apply Pattern that was not Parsed',
	'BRE015': 'Failed to Convert Year Group',
	'BRE016': 'Failed to Convert Sequence Number Group',
	'BRW001': 'Warning: Country Code not Defined',
	'BRW002': 'Warning: Document Date not Defined',
	'BRW003': 'Warning: Kind Code not Defined',
	'BRW004': 'Warning: Illegal Country Code for APP-PRI',
	'BRW005': 'Warning: XH.patentprocessingrules trigerred',
	'BRW006': 'Warning: Using Default Country Pattern',
	'BRW007': 'Warning: Country Code Replaced',
	'BRW008': 'Warning: Year Indication from RawId',
	'BRW009': 'Warning: SN Adjusted',
	'BRW010': 'Warning: Kind Code Relation not Allowed',
	'BRW011': 'Warning: Failed to Define TargetId. RawId used instead',
	'BRW012': 'Warning: Failed to Define TargetId. RawId used instead',
	'BRW013': 'Warning: Failed to Define TargetId. RawId used instead',
	'BRW014': 'No Kind Code or Generation Format Defined',
	'BRW015': 'No Date Found. Trigger lookup',
	'BRW016': 'Date Lookup Did not Find Anything',
	'BRW017': 'Year Replacement Failed. No Date Defined in the Input',
	'BRW018': 'Year Defined in Target Format, but no Date Defined',
	'BRW019': 'Document Found in DB',
	'BRW020': 'Warning: Kind code replaced by preferred lookup value',
	'BRW021': 'Warning: Kind code replaced but not with first preferred lookup value',
	'BRW022': 'Warning: Lookup found values which are not in preferred list',
	'BRW023': 'Warning: kind code lookup did not find anything',
	'BRW024': 'Warning: Lookup for kind codes with date contains more than one value',
	'BRW032': 'Warning: Unknown warning',
}

def ops_request( params ):
		# rest_version=OPS_REST_VERSION,
		# service='number-service',
		# reference='application',
		# input_type='original',
		# input='US.7654321', 
		# output_format='docdb'):

	# protocol/authority/prefix/service/reference-type/input-format/input/[endpoint]/[constituent(s)]/output-format
	url = 'http://ops.epo.org/{rest_version}/rest-services/{service}/{reference}/{input_type}/{input}/{output_format}'.format(
		rest_version 	= params['rest_version'],		
		service 		= params['service'],
		reference 		= params['reference'],
		input_type 		= params['input_type'],
		input 			= params['input'], #'US.11380365.A1.20070515',
		output_format 	= params['output_format'],
		)
	headers = {'Accept': 'application/json',}


	r = requests.get(url, headers=headers)

	return json.loads(r.text)

def expand_meta_status(status_codes):
	""" 
	Status codes should be a space-delimited string of status codes
	like those listed in NUMBER_SERVICE_STATUS
	"""
	return '\n'.join( ['{0}: {1}'.format(stat, NUMBER_SERVICE_STATUS[stat]) for stat in str(status_codes).split(' ')] )

def normalize_numberservice(rawdict, output_format):
	"""
	rawdict is a dictionary resulting from the deserialized json response from a nameservice call
	output_format can be: 'docdb' or 'epodoc'
	"""
	if output_format != 'epodoc' and output_format != 'docdb':
		return None

	##
	# Meta
	# Meta is a list of 2-element dicts of the form:
	# { u'@name': u'something', u'@value': u'something else' }
	# docdb names include 
	#	status
	#	info
	# 	version
	#	elapsed-time
	# epodoc names include 
	#	info:docdb/epodoc
	#	version:docdb/epodoc
	#	status:original/docdb
	#	elapsed-time
	meta = dict( (i['@name'], i['@value']) for i in rawdict['ops:world-patent-data']['ops:meta'])
	if output_format == 'epodoc':
		meta['info'] = meta['info:docdb/epodoc']
		meta['status'] = meta['status:original/docdb']
	meta['status'] = expand_meta_status(meta['status'])

	##
	# Output
	output = rawdict['ops:world-patent-data']['ops:standardization']['ops:output']['ops:publication-reference']['document-id']
	return dict( meta=meta, output=output )

def ops_number_request(input):
	params = {
		'rest_version' 	: OPS_REST_VERSION,		
		'service' 		: 'number-service',
		'reference' 	: 'publication', # application, priority
		'input_type' 	: 'original',
		'input' 		: '.'.join(['US', input]), #'US.11380365.A1.20070515',
		'output_format' : 'epodoc',
	}
	r = ops_request( params )
	r = normalize_numberservice(r, params['output_format'])


	# #output
	# output = r['ops:world-patent-data']['ops:standardization']['ops:output']['ops:publication-reference']['document-id']
	# for key, value in output.iteritems():
	# 	if type(value) is dict:
	# 		output[key] = value['$']
	return r



if __name__ == '__main__':
	pp = pprint.PrettyPrinter(indent=4)

	pp.pprint( ops_number_request('US7654321') )