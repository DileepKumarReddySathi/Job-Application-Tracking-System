from transitions import Machine

class ApplicationWorkflow:
    states = ["Applied", "Screening", "Interview", "Offer", "Hired", "Rejected"]

    transitions = [
        {"trigger": "next", "source": "Applied", "dest": "Screening"},
        {"trigger": "next", "source": "Screening", "dest": "Interview"},
        {"trigger": "next", "source": "Interview", "dest": "Offer"},
        {"trigger": "next", "source": "Offer", "dest": "Hired"},
        {"trigger": "reject", "source": "*", "dest": "Rejected"}
    ]

    def __init__(self, stage):
        self.machine = Machine(model=self, states=self.states, transitions=self.transitions, initial=stage)
