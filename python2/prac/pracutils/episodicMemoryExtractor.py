'''
Created on Aug 29, 2016

@author: seba
'''

import ontospy
from prac.core.base import PRAC


PRAC_ADT_URI = "http://knowrob.org/kb/acat.owl#PracAdt"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
PRAC_ADT_PROPERTY_URI = "http://knowrob.org/kb/acat.owl#" 
ACTIONCORE_URI = '{}actionCore'.format(PRAC_ADT_PROPERTY_URI)

def snake_case_to_camel_case(snake_str):
    if not snake_str: return ""
    
    words = snake_str.split('_')
    return words[0] + "".join(x.title() for x in words[1:])

def perform_triplet_query(queryHelper,x,y="?y",z="?z"):
    
    if not y.startswith("?"):
        y = "<{}>".format(y)
    if not z.startswith("?"):
        z = "<{}>".format(z)
    
    query_str = """CONSTRUCT {{ <{0}> {1} {2} }} WHERE {{ {{ <{0}> {1} {2} }} }}""".format(x,y,z)
    
    return list(g.queryHelper.rdfgraph.query(query_str))

def extract_actioncore(adt_instance, queryHelper):
    actioncore = ""
    query_result = perform_triplet_query(queryHelper,adt_instance,ACTIONCORE_URI)
    
    if query_result:
        #Assuming the query result contains only one triplet since one adt should contain only one actioncore
        actioncore_instance = query_result[0][2]
        query_result = perform_triplet_query(queryHelper,actioncore_instance,RDF_TYPE)
        
        #At the moment the actioncore is represented with the URI 'http://knowrob.org/kb/actioncore'
        for e in query_result:
            temp = e[2].split("/")[-1]
            if not temp.startswith("owl#"): 
                actioncore = temp
    
    return actioncore

def extract_actionroles(adt_instance, queryHelper,actioncore):
    prac = PRAC()
    #PRAC uses snake case to represent the actionroles
    #However the episodic memory log file uses camel case
    actionroles = map(snake_case_to_camel_case, prac.actioncores[actioncore].roles)
    extraction_result = {}
    
    for actionrole in actionroles:
        actionrole_uri = PRAC_ADT_PROPERTY_URI+actionrole 
        query_result = perform_triplet_query(queryHelper, adt_instance, actionrole_uri)
        if query_result:
            #It will be assumed that one role is only represented once in the adt
            role_owl_individual_uri = query_result[0][2]
            query_result = perform_triplet_query(queryHelper,role_owl_individual_uri,RDF_TYPE)
            #At the moment the actionrole is represented with the URI 'http://knowrob.org/kb/actionrole'
            #TODO Update this procedure if the connection to WordNet is added to the OWL files
            for e in query_result:
                temp = e[2].split("/")[-1]
                if not temp.startswith("owl#"): 
                    extraction_result[actionrole] = str(temp)
    
    return extraction_result

def process_prac_adt(adt_instance, queryHelper):
    actioncore = extract_actioncore(adt_instance, queryHelper)
    actionroles = {}
    
    if actioncore:
        actionroles = extract_actionroles(adt_instance, queryHelper, actioncore)
    
    return actionroles

if __name__ == '__main__':
    g = ontospy.Graph("chem_pipette_coll_2.owl")
    adt_instances = g.getClass(PRAC_ADT_URI).instances() 

    result = map(lambda x: process_prac_adt(x,g.queryHelper),adt_instances) 
    
    print result    