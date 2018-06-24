from prac.pracutils import StopWatch


class PRACLearning(object):
    '''
    Represents a learning step in PRAC:
    :param prac:    reference to the PRAC instance.
    '''
    
    def __init__(self, prac):
        self.prac = prac
        self.learning_steps = []
        self.microtheories = []
        self.modules = []
        self.watch = StopWatch()
        self.training_dbs = []
        self.otherParams = {}
