import requests


def do_ops():
	# protocol/authority/prefix/service/reference-type/input-format/input/[endpoint]/[constituent(s)]/output-format
	url = 'http://ops.epo.org/2.6.2/rest-services/number-service/application/original/US.11380365.A1.20070515/docdb'
	headers = {'Accept': 'application/json',}


	r = requests.get(url, headers=headers)

	return r.text


if __name__ == '__main__':
	print do_ops()