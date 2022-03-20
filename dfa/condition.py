import time

import locate

class AbsCondition:

    def __init__(self, descrip) -> None:
        self.descrip = descrip

class Condition(AbsCondition):

    def __init__(self, cond, descrip="") -> None:
        super().__init__(descrip)
        self.cond = cond    # a closure
    
    def __call__(self):
        return self.cond()

class AndCondition(AbsCondition):

    def __init__(self, conds: list, descrip="") -> None:
        super().__init__(descrip)
        self.cond_list = conds
    
    def __call__(self):
        
        result = True
        for cond in self.cond_list:
            result = result and cond()
        
        return result

class OrCondition(AbsCondition):

    def __init__(self, conds: list, descrip="") -> None:
        super().__init__(descrip)
        self.cond_list = conds
    
    def __call__(self):
        
        result = False
        for cond in self.cond_list:
            result = result or cond()
        
        return result

class TimerCondition(AbsCondition):

    def __init__(self, wait_time, descrip="") -> None:
        # wait_time: seconds
        super().__init__(descrip)

        self.wait_time = wait_time
        self.start_time = time.time()
    
    def start(self):
        self.start_time = time.time()
    
    def __call__(self):
        if time.time() - self.start_time >= self.wait_time:
            return True
        return False

class FindTemplateCondition(AbsCondition):

    def __init__(
        self,
        template_file,
        screen_file,
        pos=None,
        threshold=0.8,
        grayscale=True,
        scale_change=False,
        match_first=False,
        max_width=800,
        standard_scale=0.1,
        min_scale=0.5,
        max_scale=2.0,
        scale_interval=0.1,
        descrip=""
    ) -> None:
        # pos is None: find in whole screen
        super().__init__(descrip)

        if pos is None:
            def find():
                result = locate.search_patch(
                    template_file=template_file,
                    screen_file=screen_file,
                    threshold=threshold,
                    grayscale=grayscale,
                    scale_change=scale_change,
                    match_first=match_first,
                    max_width=max_width,
                    standard_scale=standard_scale,
                    min_scale=min_scale,
                    max_scale=max_scale,
                    scale_interval=scale_interval
                )
                if result is None:
                    return False
                return True
        else:
            def find():
                return locate.check_patch(
                    template_file=template_file,
                    screen_file=screen_file,
                    pos=pos,
                    threshold=threshold,
                    grayscale=grayscale,
                    scale_change=scale_change,
                    max_width=max_width,
                    standard_scale=standard_scale,
                    min_scale=min_scale,
                    max_scale=max_scale,
                    scale_interval=scale_interval
                )
        
        self.cond = find
    
    def __call__(self):
        return self.cond()
