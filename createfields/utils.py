"""
	Utility class for various methods
"""
from createfields.models import ErrorLog
import traceback
import datetime


def build_metadata_for_field(field_data):
	"""
		Build the metadata array for deploying a field. Different field types
		require a different Metadata array to be constructed
	"""

	field_type = field_data['type']

	# Default with metadata that all fields use
	metadata = {
		'inlineHelpText': field_data['helptext'],
        'description': field_data['description'],
        'label': field_data['label'],
        'type': field_data['type']
	}

	# Conditionally add to metadata based on field type

	if field_type == 'Checkbox':
		metadata['defaultValue'] = True if field_data['checkboxdefault'] == 'checked' else False

	elif field_type == 'Currency':
		if field_data['default']:
			metadata['default'] = field_data['default']

		metadata['precision'] = int(field_data['precision']) + int(field_data['decimal'])
		metadata['scale'] = int(field_data['decimal'])
		metadata['required'] = field_data['required']

		
	elif field_type == 'Date' or field_type == 'DateTime' or field_type == 'Phone' or field_type == 'TextArea' or field_type == 'Url':
		if field_data['default']:
			metadata['default'] = field_data['default']
		metadata['required'] = field_data['required']
		
	elif field_type == 'Email':
		if field_data['default']:
			metadata['default'] = field_data['default']
		metadata['externalId'] = field_data['external']
		metadata['required'] = field_data['required']
		metadata['unique'] = field_data['uniqueSetting']
		
	elif field_type == 'Location':
		metadata['displayLocationInDecimal'] = True if field_data['geodisplay'] == 'decimal' else False
		metadata['required'] = field_data['required']
		metadata['scale'] = int(field_data['decimal'])  if field_data['decimal'] else None

	elif field_type == 'Number':

		if field_data['default']:
			metadata['default'] = field_data['default']

		metadata['externalId'] = field_data['external']
		metadata['precision'] = int(field_data['precision']) + int(field_data['decimal'])
		metadata['scale'] = int(field_data['decimal'])
		metadata['required'] = field_data['required']
		metadata['unique'] = field_data['uniqueSetting']

	elif field_type == 'Percent':

		if field_data['default']:
			metadata['default'] = field_data['default']

		metadata['precision'] = int(field_data['precision']) + int(field_data['decimal'])
		metadata['scale'] = int(field_data['decimal'])
		metadata['required'] = field_data['required']
		metadata['unique'] = field_data['uniqueSetting']

	elif field_type == 'Picklist':
		metadata['picklist'] = build_picklist_values(field_data)

	elif field_type == 'MultiselectPicklist':
		metadata['visibleLines'] = field_data['vislines']
		metadata['picklist'] = build_picklist_values(field_data)

	elif field_type == 'Text':
		if field_data['default']:
			metadata['default'] = field_data['default']
		metadata['length'] = field_data['length']
		metadata['externalId'] = field_data['external']
		metadata['required'] = field_data['required']
		metadata['unique'] = field_data['uniqueSetting']

	elif field_type == 'LongTextArea':
		if field_data['default']:
			metadata['default'] = field_data['default']
		metadata['length'] = field_data['length']
		metadata['visibleLines'] = field_data['vislines']

	elif field_type == 'Html':
		metadata['length'] = field_data['length']
		metadata['visibleLines'] = field_data['vislines']

	elif field_type == 'EncryptedText':
		metadata['length'] = field_data['length']
		metadata['required'] = field_data['required']
		metadata['maskChar'] = field_data['maskchar']
		metadata['maskType'] = field_data['masktype']


	return metadata


def build_picklist_values(field_data):
	"""
		Method to build picklist JSON from page
	"""

	# Parse full string from POST message
	picklist_values = field_data['picklistvalues']

	# start empty array
	picklist_values_list = []

	# JSON list
	picklist_json_list = []

	try:
		
		# Split string for new lines
		for value in picklist_values.split('\n'):

			# Trim any whitesapce
			value = value.strip()

			# If value isn't blank or null, add to array
			if value:

				picklist_values_list.append(value)

		# Determine first value for the loop
		first_value = True

		# Start building JSON picklist array
		for picklist in picklist_values_list:

			# Build picklist value
			json_dict = {
				'valueName': picklist,
				'default': True if first_value and field_data['firstvaluedefault'] else False # If first value and first value default is checked
			} 

			# Add dict to list
			picklist_json_list.append(json_dict)	

			# Remove the first value boolean
			first_value = False

	except Exception as ex:
		# TODO - error handling
		create_error_log('Picklist Error', ex)		

	picklist = {
		'picklistValues': picklist_json_list,
		'sorted': field_data['sortalpha']
	}

	return picklist


def create_error_log(name, error):
	"""
		Method to create an error log record
	"""

	error_log = ErrorLog()
	error_log.created_date = datetime.datetime.now()
	error_log.name = name
	error_log.error = error
	error_log.save()


def chunks(l, n):
	"""
		Split a list into specified chunks
	"""
	n = max(1, n)
	return [l[i:i + n] for i in range(0, len(l), n)]
