'''
Created on Sep 2, 2015

@author: seba
'''

import os
import traceback
from collections import defaultdict
from pprint import pprint

import pymongo

from ...core.inference import PRACInference
from .models import Frame, Word, Howto, Object, constants


def __dividedict(d, dnew):
    if not d: 
        yield dnew
        return
    key, values = d.popitem()
    for v in values:
        dnew_ = dict(dnew)
        dnew_[key] = v
        for d_ in __dividedict(dict(d), dnew_): yield d_

def ddivide(d):
    return __dividedict(d, {})


class HowtoImport(object):
    '''
    '''

    def __init__(self, prac, howto):
        self.howto = howto
        self.prac = prac


    def run(self):
        instr, steps = dict(self.howto).popitem()
        howto = self.buildhowto(instr, steps)
        if howto is not None:
            pprint(howto.tojson())
            self.prac.mongodb.prac.howtos.insert_one(howto.tojson())
        print(howto.shortstr())
    
    
    def buildframes(self, db, sidx, sentence):
        for p, args in db.syntax():
            print(p, args)
        for _, actioncore in db.actioncores():
            roles = defaultdict(list)
            for role, word in db.rolesw(actioncore):
                sense = db.sense(word)
                props = db.properties(word)
                obj = Object(self.prac, id_=word, type_=sense, props=props, syntax=self.buildword(db, word))
                roles[role].append(obj)
            frames = ddivide(roles)    
            for frame in frames:
                yield Frame(self.prac, sidx, sentence, syntax=list(db.syntax()), words=self.buildwords(db), actioncore=actioncore, actionroles=frame)
    
    
    def buildword(self, db, word):
        tokens = word.split('-')
        w = '-'.join(tokens[:-1])
        idx = int(tokens[-1])
        pos = set(db.postag(word)).pop()
        sense = db.sense(word)
        nltkpos = db.prac.wordnet.nltkpos(pos)
        lemma = db.prac.wordnet.lemmatize(w, nltkpos) if nltkpos is not None else None
        return Word(self.prac, word, w, idx, sense, pos, lemma)
    
                
    def buildwords(self, db):
        for word in db.words():
            yield self.buildword(db, word)
            
        
        
    def buildhowto(self, instr, steps):
        '''
        constructs a json representation of the instruction ``instr`` 
        '''
        stopmodules = ('role_look_up', 'achieved_by', 'complex_achieved')
        infer = PRACInference(self.prac, instr).run(stopmodules)
        mainresult = [db for step in infer.steps() for db in step.outdbs] #self.prac.query(instr, stopat=stopmodules).inf_steps[-1].output_dbs
        for step in infer.steps(): 
            mainframe = step.frame
        infer = PRACInference(self.prac, steps).run(stopmodules)
        stepresults = [db for step in infer.steps() for db in step.outdbs]#self.prac.query(steps, stopat=stopmodules).inference_steps[-1]
#         mainframe = self.buildframes(mainresult[0], 0, instr)
        frames = [] 
        for step in infer.steps():
            frames.append(step.frame)
        return Howto(self.prac, instr=mainframe, steps=frames)
    
    
    def store_frames_into_database(self, howto, frames):
        pracdb = self.prac.mongodb.prac
        howtos = pracdb.howtos
        steps = []
        actioncore = None
        roles = {}
        try:
            #Parse text file name to annotate it in the mongo db
            inference = PRACInference(self.prac, ["{}.".format(os.path.basename(howto))])
            
            while inference.next_module() not in ('role_look_up', 'achieved_by', 'plan_generation'):
                modulename = inference.next_module()
                module = self.prac.module(modulename)
                self.prac.run(inference, module)
        
            db = inference.inference_steps[-1].output_dbs[0]
            
            for result_ac in db.actioncores():
                for result_role in db.roles(list(result_ac.values()).pop()):
                    roles[list(result_role.keys())[0]] = list(result_role.values())[0]
            # we assume that there is only one true action_core predicate per database 
            for _, actioncore in db.actioncores(): break
        except:
            actioncore = None
        for frame in frames:
            steps.append(frame.json)
        try:
            document = {'_id' : text_file_name,
                        constants.JSON_HOWTO_ACTIONCORE : actioncore, 
                        constants.JSON_HOWTO_ACTIONROLES : roles,
                        constants.JSON_HOWTO_STEPS : steps}
            howtos.insert_one(document)
        except pymongo.errors.DuplicateKeyError:
            howtos.delete_many({"_id" : document['_id']})
            howtos.insert_one(document)
        except:
            traceback.print_exc()
            

    