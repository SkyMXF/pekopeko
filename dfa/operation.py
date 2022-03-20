import time

import adb
from dfa.condition import AbsCondition

class Operation:

    def __init__(self, descrip) -> None:
        self.descrip = descrip
        self.op = lambda : None
    
    def __call__(self):
        self.op()

class TapOperation(Operation):

    def __init__(self, runner: adb.AdbRunner, pos, device, delay=1.0, descrip="") -> None:
        super().__init__(descrip)

        def run():
            time.sleep(delay)
            runner.tap(pos=pos, dev=device, norm_pos=True)
        
        self.op = run

class DelayOperation(Operation):

    def __init__(self, delay, descrip="") -> None:
        # delay: seconds
        super().__init__(descrip)

        def run():
            time.sleep(delay)
        
        self.op = run

class SequentialOperation(Operation):

    def __init__(self, ops: list, descrip="") -> None:
        super().__init__(descrip)

        def run():
            for op in ops:
                op()
        
        self.op = run

class ForOperation(Operation):

    def __init__(self, op, times, descrip="") -> None:
        super().__init__(descrip)

        def run():
            for _ in range(times):
                op()
        
        self.op = run

class IfOperation(Operation):

    def __init__(self, cond: AbsCondition, true_op, false_op, descrip="") -> None:
        super().__init__(descrip)

        def run():
            if cond():
                true_op()
            else:
                false_op()
        
        self.op = run