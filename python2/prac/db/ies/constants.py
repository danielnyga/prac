'''
Created on Sep 3, 2015

@author: seba
'''

SLOT_VALUE_PREDICATE = 'predicate'
SLOT_VALUE_DOBJ = 'dobj'
SLOT_VALUE_NSUBJ = 'nsubj'
SLOT_VALUE_IOBJ = 'iobj'
SLOT_VALUE_PREPOBJ = 'prepobj'

SLOT_VALUES = [SLOT_VALUE_PREDICATE,
               SLOT_VALUE_DOBJ,
               SLOT_VALUE_NSUBJ,
               SLOT_VALUE_IOBJ,
               SLOT_VALUE_PREPOBJ]

PREDICATE_MLN_PREDICATE = '{}({{}})'.format(SLOT_VALUE_PREDICATE)
NSUBJ_MLN_PREDICATE = '{}({{}},{{}})'.format(SLOT_VALUE_NSUBJ)
DOBJ_MLN_PREDICATE = '{}({{}},{{}})'.format(SLOT_VALUE_DOBJ)
IOBJ_MLN_PREDICATE = '{}({{}},{{}})'.format(SLOT_VALUE_IOBJ)
PREPOBJ_MLN_PREDICATE = '{}({{}},{{}})'.format(SLOT_VALUE_PREPOBJ)
HAS_POS_MLN_PREDICATE = 'has_pos({},{})'
IS_A_MLN_PREDICATE = 'is_a({},{})'
HAS_SENSE_MLN_PREDICATE = 'has_sense({},{})'


JSON_SENSE_WORD = 'word'
JSON_SENSE_LEMMA = 'lemma'
JSON_SENSE_PENN_TREEBANK_POS = 'penn_treebank_pos'
JSON_SENSE_POS = 'pos'
JSON_SENSE_WORDNET_POS = 'wordnet_pos'
JSON_SENSE_NLTK_WORDNET_SENSE = 'nltk_wordnet_sense'
JSON_SENSE_SENSE = 'sense'
JSON_SENSE_WORD_IDX = 'widx'
JSON_SENSE_MISC = 'misc'
JSON_SENSE_WORD_ID = 'wid'
#------------------------------------------------------------------------------ 
JSON_FRAME_ID = '_id'
JSON_FRAME_SENTENCE_IDX = 'sidx'
JSON_FRAME_SENTENCE = 'sentence'
JSON_FRAME_PRAC_MLN = 'prac_mln'
JSON_FRAME_PRAC_DB = 'prac_db'
JSON_FRAME_SYNTAX = 'syntax'
JSON_FRAME_ACTIONCORE = 'actioncore'
JSON_FRAME_ACTIONCORE_ROLES = 'actionroles'
JSON_FRAME_WORDS = 'words'
#------------------------------------------------------------------------------ 
JSON_HOWTO_STEPS = 'steps'
JSON_HOWTO_ACTIONROLES = JSON_FRAME_ACTIONCORE_ROLES
JSON_HOWTO_ACTIONCORE = JSON_FRAME_ACTIONCORE
JSON_HOWTO_INSTRUCTION = 'howto'
JSON_HOWTO_SYNTAX = 'syntax'
JSON_HOWTO_IMPORT_DATE = 'import_date'
#------------------------------------------------------------------------------ 
JSON_OBJECT_TYPE = 'type'
JSON_OBJECT_ID = 'id'
JSON_OBJECT_PROPERTIES = 'properties'
JSON_OBJECT_SYNTAX = 'syntax' 
#------------------------------------------------------------------------------ 
JSON_PROCESS_TEXT_FILE_RESULT_ID = JSON_FRAME_ID
JSON_PROCESS_TEXT_FILE_RESULT_NUM_PARSING_ERROR_SENTENCES = 'num_parsing_error_sentences'
JSON_PROCESS_TEXT_FILE_RESULT_NUM_NO_PREDICATE_SENTENCES = 'num_no_predicate_sentences'
JSON_PROCESS_TEXT_FILE_RESULT_NUM_NO_VALID_FRAME_SENTENCES = 'num_no_valid_frame_sentences'
JSON_PROCESS_TEXT_FILE_RESULT_NUM_EXTRACTED_FRAMES = 'num_extracted_frames'
JSON_PROCESS_TEXT_FILE_RESULT_NUM_SENTENCES = 'num_sentences'
JSON_PROCESS_TEXT_FILE_RESULT_NUM_ERRORS = 'num_errors'
JSON_PROCESS_TEXT_FILE_RESULT_NUM_NOUNS = 'num_nouns'
JSON_PROCESS_TEXT_FILE_RESULT_NUM_VERBS = 'num_verbs'
JSON_PROCESS_TEXT_FILE_RESULT_NUM_ADJS = 'num_adjs'
JSON_PROCESS_TEXT_FILE_RESULT_NUM_UNK = 'num_unk'
JSON_PROCESS_TEXT_FILE_RESULT_NUM_ASSERT_SENSES = 'num_assert_senses'
JSON_PROCESS_TEXT_FILE_RESULT_NO_PREDICATE_SENTENCES = 'no_predicate_sentences'
JSON_PROCESS_TEXT_FILE_RESULT_NO_VALID_FRAME_SENTENCES = 'no_valid_frame_sentences'
JSON_PROCESS_TEXT_FILE_RESULT_PARSING_ERROR_SENTENCES = 'parsing_error_sentences'
#------------------------------------------------------------------------------ 
JSON_LOG_FILE_SENTENCE_REPRESENTATION_SENTENCE = JSON_FRAME_SENTENCE
JSON_LOG_FILE_SENTENCE_REPRESENTATION_PRAC_MLN = JSON_FRAME_PRAC_MLN
JSON_LOG_FILE_SENTENCE_REPRESENTATION_PRAC_DB = JSON_FRAME_PRAC_DB
