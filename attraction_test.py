from equation_parser import Parser
from attraction import attract
from utils import trace

def test_basic_attraction():
    #Arrange
    #TODO: Remove parser dependency here to avoid error cascade
    #in event of parser failures
    tree = Parser("x+2+x=1").parse()
    attract(tree) 
    assert trace(tree) == "((x+x)+2)=1" 


    
