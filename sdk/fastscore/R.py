# Python utils used by the R package.
import json
import fastscore.datatype
from fastscore.datatype import jsonEncoder, jsonDecoder, avroTypeToSchema, jsonToAvroType, checkData
from fastscore.utils import ts
import fastscore.errors
import avro.schema
import re

def _R_to_json(datum, schema):
    """
    A utility function used for the R to JSON conversions.
    Python applications should use the to_json() function defined
    elsewhere in this package.
    """
    return json.dumps(jsonEncoder(jsonToAvroType(schema), datum))

def _R_from_json(datum, schema):
    """
    A utility function used for the R from JSON conversions.
    Python applications should use the from_json() function defined
    elsewhere in this package.
    """
    return jsonDecoder(jsonToAvroType(schema), json.loads(datum))

def _R_checkData(datum, schema, use_json):
    """
    A schema-conformance checker used by the R libraries.
    Python applications should use the Titus checkData function.
    """
    mysch = jsonToAvroType(schema)
    result = False
    try:
        if(use_json):
            result = checkData(json.loads(datum), mysch)
        else:
            result = checkData(datum, mysch)
        return result != False
    except TypeError:
      return False

def _R_split_functions(r_str):
    """
    A function to split a single R source file into
    its component import statements, functions, and FastScore options.
    """
    options = {} # e.g. input: input_schema
    libs = [] # a list of strings
    fcns = [] # a list of dictionaries: {"name":"action", "def":"function(datum){ emit(datum)}"}
    lines = r_str.split('\n')
    fcn_str = ''
    fcn_name = ''
    levels = 0
    for line in lines:
        # extract options:
        option = re.search(r'# *fastscore\.(.*):(.*)', line.strip())
        if option:
            option_name = option.group(1).strip()
            option_value = option.group(2).strip()
            options[option_name] = option_value
        # extract libraries
        if re.match(r'library\(.*\)', line):
            libs += [line.strip()]
        # extract functions:
        if '#' in line:
            clean_line = ''.join(line.split('#')[:-1]) # remove comments
        else:
            clean_line = line
        match = re.match(r'(.*)<-.*function\(', clean_line) # find fcn def's
        if match or '{' in clean_line:
            if levels == 0:
                fcn_name = match.group(1).strip() # if it's a top-level fcn, name it
            levels += 1
        if levels > 0:
            fcn_str += line + '\n' # we include the original line, to capture comments
        if '}' in clean_line:
            levels -= 1
            if levels == 0:
                fcn_str = ''.join(fcn_str.split('<-')[1:]).strip()
                fcns += [{'name':fcn_name, 'def':fcn_str}]
                fcn_str = ''
                fcn_name = ''
    return {'fcns':fcns, 'options':options, 'libs':libs}
