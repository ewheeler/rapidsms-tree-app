from rapidsms.tests.scripted import TestScript
from app import App
import apps.reporters.app as reporters_app
from models import *


    
class TestApp (TestScript):
    apps = (App, reporters_app.App)
    # the test_backend script does the loading of the dummy backend that allows reporters
    # to work properly in tests
    fixtures = ['test_backend']
    

    
    def setUp(self):
        TestScript.setUp(self)
        if not self.isSetup():
            question_strings = ["hello", "Please enter your 4-digit PIN", "Thanks for entering."]
            questions = []
            for question_text in question_strings:
                question = Question(text=question_text)
                question.save()
                questions.append(question)
            state_names = ["test_root" , "test_pin" , "pin_success" ]
            state_map = { state_names[0]: questions[0], state_names[1] : questions[1], state_names[2] : questions[2]}
            states = []
            for name in state_names:
                state = TreeState(name=name, question=state_map[name])
                state.save()
                states.append(state)
            trees = { "test" : states[0], "pin" : states[1]}
            for trigger, state in trees.items():
                tree = Tree(trigger=trigger, root_state=state)
                tree.save()
            transition = Transition(current_state=states[1], next_state=states[2], type="R", answer=r"^(\d{4})$", description="a 4-digit decimal number")
            transition.save()
            
            

    def isSetup(self):
        return len(Tree.objects.all()) > 0
    
    testTrigger = """
           8005551212 > test
           8005551212 < hello
         """        
    
    testPin = """
           8005551211 > pin
           8005551211 < Please enter your 4-digit PIN
           8005551211 > 1234
           8005551211 < Thanks for entering.
         """
         
    testPinFailure = """
           8005551213 > pin
           8005551213 < Please enter your 4-digit PIN
           8005551213 > abcd
           8005551213 < "abcd" is not a valid answer. You must enter a 4-digit decimal number
           8005551213 > 123
           8005551213 < "123" is not a valid answer. You must enter a 4-digit decimal number
           8005551213 > 123d
           8005551213 < "123d" is not a valid answer. You must enter a 4-digit decimal number
           8005551213 > 12345
           8005551213 < "12345" is not a valid answer. You must enter a 4-digit decimal number
           8005551213 > 
           8005551213 < "" is not a valid answer. You must enter a 4-digit decimal number
           8005551213 > 0000
           8005551213 < Thanks for entering.
         """