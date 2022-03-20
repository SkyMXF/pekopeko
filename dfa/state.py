#from .transition import Transition
#from .operation import Operation

class UnknownStateError(Exception):

    def __init__(self, info):
        super().__init__(self)
        self.info = info

    def __str__(self):
        return self.info

class State:

    def __init__(self, descrip, operation = None, transition = None) -> None:
        self.descrip = descrip
        self.operation = operation
        self.transition = transition
    
    def run(self):
        self.operation()
    
    def next(self):
        if self.transition is None:
            raise UnknownStateError("No state after '%s'"%(self.descrip))

        next_state = self.transition.forward()
        if next_state is None:
            raise UnknownStateError("No state after '%s'"%(self.descrip))
        
        return next_state
    
    