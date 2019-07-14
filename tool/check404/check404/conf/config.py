#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DateTime    : 2019-07-06 17:43:46
# Author  : dongchuan
# Version : v1.0
# Desc     : 

class Config(object):
	MAX_STABILITY_DELAY = 0.5
	BOUNDARY_BACKSLASH_MARKER = '__BACKSLASH__'
	CUSTOM_INJECTION_MARK_CHAR = '*'
	DEFAULT_GET_POST_DELIMITER = '&'
	URI_QUESTION_MARKER = "__QUESTION_MARK__"
	DYNAMICITY_MARK_LENGTH = 32
	PARAMETER_AMP_MARKER = '__AMP__'
	PARAMETER_SEMICOLON_MARKER = '__SEMICOLON__'
	UNICODE_ENCODING = 'utf8'
	HEURISTIC_CHECK_ALPHABET = ('"', '\'', ')', '(', ',', '.')
	URLENCODE_CHAR_LIMIT = 2000
	URLENCODE_FAILSAFE_CHARS = "()|,"
	REFLECTED_VALUE_MARKER = "__REFLECTED_VALUE__"
	TEXT_TAG_REGEX = r"(?si)<(abbr|acronym|b|blockquote|br|center|cite|code|dt|em|font|h\d|i|li|p|pre|q|strong|sub|sup|td|th|title|tt|u)(?!\w).*?>(?P<result>[^<]+)"
	
