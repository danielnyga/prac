import os

from collections import defaultdict
from dnutils import logs, out, ifnone
from pracmln import MLNQuery
from pracmln.mln.base import parse_mln
from pracmln.utils.project import MLNProject

from prac.core.base import PRACModule, PRACDatabase
from prac.core.inference import PRACInferenceStep, FrameNode
from prac.db.ies.models import Object, Frame
from prac.pracutils.utils import prac_heading, splitd

logger = logs.getlogger('/prac/grounding')


def newsymbol(mln, db, domain):
    symbols = mln.domains.get(domain, []) + db.domains.get(domain, [])
    i = 0
    while 1:
        s = 'skolem-%d' % i
        i += 1
        if s not in symbols:
            return s


class Grounding(PRACModule):

    def __call__(self, infer, worldmodel, constraints=None):
        return self.deterministic_grounding(infer, worldmodel, constraints)

    def deterministic_grounding(self, infer, worldmodel, constraints):
        newframes = []
        frames = [n.frame for n in infer.steps()]
        for frame in frames:
            skipframe = False
            for role, obj in frame.actionroles.items():
                frame.actionroles[role].type = list(set([o.type for o in worldmodel.getall(obj)]))
                # out(frame.toplan(), frame.actionroles[role].type)
                if not frame.actionroles[role].type:
                    if not frame.mandatory:
                        out('skipping frame', frame.toplan(), 'because it is not mandatory')
                        skipframe = True
                        break
                    else:
                        raise Exception(str(frame.toplan()) + ' is not executable.')
            if skipframe:
                continue
            queue = [frame]
            while queue:
                f = queue.pop(0)
                modified = False
                for role, obj in f.actionroles.items():
                    if type(obj.type) is list:
                        f_ = None
                        if len(obj.type) == 1:
                            obj.type = obj.type[0]
                        else:
                            f_ = f.copy()
                            f_.actionroles[role].type = obj.type.pop()
                            modified = True
                    if modified:
                        queue.append(f)
                        queue.append(f_)
                        break
                if not modified:
                    newframes.append(f)
        return newframes

    def probabilistic_grounding(self, node, worldmodel, constraints):
        logger.info('{} {}'.format(self.name, node))
        constraints = ifnone(constraints, {})
        self.roles = self.prac.module('senses_and_roles')
        self.wnmod = self.prac.module('wn_senses')

        # get the actioncore and pramcln project
        actioncore = self.prac.actioncores[node.frame.actioncore]
        logger.debug('Loading Project: {}.pracmln'.format(actioncore.name))
        projectpath = os.path.join(self.roles.module_path, '{}.pracmln'.format(actioncore.name))
        try:
            project = MLNProject.open(projectpath)
        except IOError as err:
            logger.error('could not lod pracmln project: %s. skipping this reasoning task.' % str(err))
            return

        # get the queries stored in the pracmln project
        mlntext = project.mlns.get(project.queryconf['mln'], None)

        mln = parse_mln(mlntext,
                        searchpaths=[self.roles.module_path],
                        projectpath=projectpath,
                        logic=project.queryconf.get('logic', 'FuzzyLogic'),
                        grammar=project.queryconf.get('grammar', 'PRACGrammar'))

        # ==============================================================
        # Preprocessing
        # ==============================================================
        # collect the objects from the db
        objects = []
        types = set()
        for s in objdb.query('instance_of(?id, ?concept)'):
            objects.append({s['?id']: s['?concept']})
            types.add(s['?concept'])
        logger.debug('collected world model from db:', objects)

        # collect the known roles
        role2concept = {str(role): str(o.type) for role, o in node.frame.actionroles.items() if o.type in types}
        concept2role = {str(o.type): str(role) for role, o in node.frame.actionroles.items() if o.type in types}
        logger.info('creating evidence database for %s' % objects)
        # out(concept2role)
        # out(role2concept)
        db = PRACDatabase(self.prac)
        # db << 'action_core(actioncore, %s)' % actioncore.name
        for obj in objects:
            for id_, concept in obj.items():
                db << 'has_sense(%s, %s)' % (id_, concept)
                db << 'is_a(%s,%s)' % (concept, concept)
                if concept in concept2role: # here come the exactly matching instances
                    db << '%s(%s,%s)' % (concept2role[concept], id_, actioncore.name)
        project.queryconf['cw'] = True
        project.queryconf['queries'] = [r for r in actioncore.roles if r != 'action_verb']  #  if r not in role2concept]
        # copy over the role constraints
        # TODO: this hs to go into the ROS module
        for role, concepts in constraints.items():
            for concept in concepts:
                for s in db.query('has_sense(?id, ?s) ^ is_a(?s,%s)' % concept):
                    out('asserting', str(role), str(s['?id']), str(actioncore.name))
                    db << '%s(%s,%s)' % (str(role), str(s['?id']), str(actioncore.name))
        tmpmln = mln.copy()
        tmpmln.domains['concept'] = list(set(tmpmln.domains['concept']) | set(db.domains['concept']))
        simil = self.wnmod.add_sims(db, tmpmln)
        # we need senses and similarities as well as original evidence
        db = db.union(simil)
        db.write(bars=False, color=False)
        out(project.queryconf['queries'])
        infer = MLNQuery(config=project.queryconf, mln=mln, db=db, verbose=1).run()
        resultdb = PRACDatabase(self.prac, db=infer.resultdb)
        resultdb.write()
        resultdb = db.union(resultdb, mln=self.prac.mln)
        # ==============================================================
        # Postprocessing
        # ==============================================================
        for role, concept in resultdb.roles(actioncore.name):
            yield role, concept

