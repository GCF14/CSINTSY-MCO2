from pyswip import Prolog
import re


prolog = Prolog()


prolog.consult("chatbot.pl")


def assert_fact(fact):

    try:
        if not list(prolog.query(fact)):
            prolog.assertz(fact)
            # print(f"Asserted: {fact}") This is for debugging keep it in case we need to track results later
    except Exception as e:
        print(f"Error asserting fact '{fact}': {e}")

def process_sibling_relationship(message):
    
    pattern = r"(\w+)\s+and\s+(\w+)\s+are\s+siblings"
    match = re.search(pattern, message)
    
    
    if match:
        
        name1 = match.group(1)
        name2 = match.group(2)
        if name1 != name2:
      
            assert_fact(f"siblings('{name1}', '{name2}')")
            assert_fact(f"siblings('{name2}', '{name1}')")
            print(f"OK! I learned that {name1} and {name2} are siblings.\n")

           
           
            parent1 = list(prolog.query(f"parent(P, '{name1}')"))
            parent2 = list(prolog.query(f"parent(P, '{name2}')"))
            
            
            if parent1 and parent2:
                parent = parent1[0]["P"]
                if parent != parent2[0]["P"]:
                    print("Both siblings have different parents.")
            elif parent1:
                parent = parent1[0]["P"]
                assert_fact(f"parent('{parent}', '{name2}')")
               
            elif parent2:
                parent = parent2[0]["P"]
                assert_fact(f"parent('{parent}', '{name1}')")
        else:
            print(f"Error: {name1} cannot be a sibling of themselves.")
            
            
        return True
    
    return False


def process_parent_relationship(message):
    
    pattern = r"(\w+)\s+is\s+a\s+child\s+of\s+(\w+)"
    match = re.search(pattern, message)
    
    if match:
        child = match.group(1)
        parent = match.group(2)
   
        assert_fact(f"parent('{parent}', '{child}')")
        print(f"OK! I learned that {parent} is a parent of {child}.\n")
        
    
        siblings = list(prolog.query(f"parent('{parent}', Sibling), Sibling \\= '{child}'"))
        
        for sibling in siblings:
            sibling_name = sibling["Sibling"]
            assert_fact(f"siblings('{child}', '{sibling_name}')")
            assert_fact(f"siblings('{sibling_name}', '{child}')")
           
        
 
        siblings = list(prolog.query(f"siblings('{child}', Sibling)"))
        
        for sibling in siblings:
            sibling_name = sibling["Sibling"]
            if sibling_name != child:
                if not list(prolog.query(f"parent('{parent}', '{sibling_name}')")):
                    assert_fact(f"parent('{parent}', '{sibling_name}')")
                   
        return True
    
    return False


def process_sibling_query(message):
    
    pattern = r"Are\s+(\w+)\s+and\s+(\w+)\s+siblings\?"
    match = re.search(pattern, message)
    
    if match:
        name1 = match.group(1)
        name2 = match.group(2)
        result = list(prolog.query(f"siblings('{name1}', '{name2}')"))
        
        
        if result:
            print(f"Yes, {name1} and {name2} are siblings.\n")
        else:
            print(f"No, {name1} and {name2} are not siblings.\n")
            
            
        return True
    
    
    return False

def process_child_query(message):
    
    pattern = r"Is\s+(\w+)\s+a\s+child\s+of\s+(\w+)\?"
    match = re.search(pattern, message)
    
    if match:
        child = match.group(1)
        parent = match.group(2)
        result = list(prolog.query(f"parent('{parent}', '{child}')"))
        
        
        if result:
            print(f"Yes, {child} is a child of {parent}.\n")
            
        else:
            print(f"No, {child} is not a child of {parent}.\n")
            
            
        return True
    
    
    return False


def main():
    
    while True:
        
        message = input("Enter your message: ").strip()
        
        if process_sibling_relationship(message):
            continue
        elif process_parent_relationship(message):
            continue
        elif process_sibling_query(message):
            continue
        elif process_child_query(message):
            continue
        elif re.search(r"I\s+would\s+like\s+to\s+stop\s+talking\s+now", message, re.IGNORECASE):
            print("Goodbye!")
            break
        else:
            print("Sorry, I didn't understand that. Please try again.\n")


if __name__ == "__main__":
    main()