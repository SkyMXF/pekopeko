import time

from dfa.condition import AbsCondition
from dfa.state import State

class Transition:

    def __init__(self) -> None:
        pass
    
    def forward(self):
        return None

class SequentialTransition(Transition):

    def __init__(self, aim_state: State) -> None:
        super().__init__()
        self.aim_state = aim_state
    
    def forward(self):
        return self.aim_state

class CondTimeOutError(Exception):

    def __init__(self, info):
        super().__init__(self)
        self.info = info

    def __str__(self):
        return self.info

class CondTransition(Transition):

    def __init__(
        self,
        aim_state: State, cond: AbsCondition,
        retry_interval: float = 1.0, max_retry: int = 10
    ) -> None:
        super().__init__()

        self.aim_state = aim_state
        self.cond = cond
        self.retry_interval = retry_interval
        self.max_retry = max_retry
    
    def forward(self):
        return self.wait_until()
    
    def check_once(self):
        if self.cond():
            return self.aim_state
        else:
            return None
    
    def wait_until(self):
        for _ in range(self.max_retry):
            if self.cond():
                return self.aim_state
            time.sleep(self.retry_interval)
        
        raise CondTimeOutError("Timeout for condition '%s'."%(self.cond.descrip))

class MultiCondTransition(Transition):

    def __init__(
        self,
        aim_states: list, conds: list,
        retry_interval: float = 1.0, max_retry: int = 10
    ) -> None:
        super().__init__()

        self.aim_states = aim_states
        self.conds = conds
        self.retry_interval = retry_interval
        self.max_retry = max_retry
    
    def forward(self):
        return self.wait_until()
    
    def check_once(self):
        for state_idx in range(len(self.aim_states)):
            if self.conds[state_idx]():
                return self.aim_states[state_idx]
        return None
    
    def wait_until(self):
        for _ in range(self.max_retry):
            for state_idx in range(len(self.aim_states)):
                if self.conds[state_idx]():
                    return self.aim_states[state_idx]
            time.sleep(self.retry_interval)
        
        raise CondTimeOutError("Timeout for condition '%s'."%(self.cond.descrip))
        