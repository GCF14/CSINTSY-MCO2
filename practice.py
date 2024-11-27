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
            
            
            # Get the siblings of name1 and name2
            siblings_of_name1 = list(prolog.query(f"siblings('{name1}', Sibling), Sibling \\= '{name1}'"))
            siblings_of_name2 = list(prolog.query(f"siblings('{name2}', Sibling), Sibling \\= '{name2}'"))
            
            
           
            for sibling in siblings_of_name1:
                sibling_name = sibling["Sibling"]
                if sibling_name != name2:
                    if not list(prolog.query(f"siblings('{name2}', '{sibling_name}')")):
                        assert_fact(f"siblings('{name2}', '{sibling_name}')")
                    if not list(prolog.query(f"siblings('{sibling_name}', '{name2}')")):
                        assert_fact(f"siblings('{sibling_name}', '{name2}')")
                    if list(prolog.query(f"female('{sibling_name}')")):
                        if not list(prolog.query(f"sister('{name2}', '{sibling_name}')")):
                            assert_fact(f"sister('{name2}', '{sibling_name}')")
            
            for sibling in siblings_of_name2:
                sibling_name = sibling["Sibling"]
                if sibling_name != name1:
                    if not list(prolog.query(f"siblings('{name1}', '{sibling_name}')")):
                        assert_fact(f"siblings('{name1}', '{sibling_name}')")
                    if not list(prolog.query(f"siblings('{sibling_name}', '{name1}')")):
                        assert_fact(f"siblings('{sibling_name}', '{name1}')")
                    if list(prolog.query(f"female('{sibling_name}')")):
                        if not list(prolog.query(f"sister('{name1}', '{sibling_name}')")):
                            assert_fact(f"sister('{name1}', '{sibling_name}')")

           
           
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
                
            
            # Check if one of the siblings has a grandfather
            grandfathers_of_name1 = list(prolog.query(f"grandfather(Grandfather, '{name1}')"))
            grandfathers_of_name2 = list(prolog.query(f"grandfather(Grandfather, '{name2}')"))
            
            for grandfather in grandfathers_of_name1 + grandfathers_of_name2:
                grandfather_name = grandfather["Grandfather"]
                if not list(prolog.query(f"grandfather('{grandfather_name}', '{name1}')")):
                    assert_fact(f"grandfather('{grandfather_name}', '{name1}')")
                if not list(prolog.query(f"grandfather('{grandfather_name}', '{name2}')")):
                    assert_fact(f"grandfather('{grandfather_name}', '{name2}')")
                
                # Get the siblings of name1 and name2
                siblings_of_name1 = list(prolog.query(f"siblings('{name1}', Sibling), Sibling \\= '{name1}'"))
                siblings_of_name2 = list(prolog.query(f"siblings('{name2}', Sibling), Sibling \\= '{name2}'"))
                
                for sibling in siblings_of_name1 + siblings_of_name2:
                    sibling_name = sibling["Sibling"]
                    if not list(prolog.query(f"grandfather('{grandfather_name}', '{sibling_name}')")):
                        assert_fact(f"grandfather('{grandfather_name}', '{sibling_name}')")
                        
        else:
            print(f"Error: {name1} cannot be a sibling of themselves.")
            
            
        return True
    
    return False


def process_father_relationship(message):
    # Regular expression to extract father relationships
    pattern = r"(\w+)\s+is\s+the\s+father\s+of\s+(\w+)"
    match = re.search(pattern, message)
    
    if match:
        # Extract names from the message
        father = match.group(1)
        child = match.group(2)
        
        existing_father = list(prolog.query(f"father(Father, '{child}')"))
        if existing_father:
            # If an existing father is found, return a message and skip assertion
            current_father = existing_father[0]["Father"]  # Get the current father
            print(f"{child} already has a father: {current_father}.\n")
            return True

        # Assert the fact into the Prolog database
        assert_fact(f"father('{father}', '{child}')")
        assert_fact(f"parent('{father}', '{child}')")
        assert_fact(f"male('{father}')")
        
        print(f"OK! I learned that {father} is a parent(father) of {child}.\n")

        siblings = list(prolog.query(f"father('{father}', Sibling), Sibling \\= '{child}'"))
        
        for sibling in siblings:
            sibling_name = sibling["Sibling"]
            assert_fact(f"siblings('{child}', '{sibling_name}')")
            assert_fact(f"siblings('{sibling_name}', '{child}')")
           
        
 
        siblings = list(prolog.query(f"siblings('{child}', Sibling)"))
        
        for sibling in siblings:
            sibling_name = sibling["Sibling"]
            if sibling_name != child:
                if not list(prolog.query(f"parent('{father}', '{sibling_name}')")):
                    assert_fact(f"parent('{father}', '{sibling_name}')")
        return True
    
    return False

def process_father_query(message):
    # Regular expression to extract the father and child from the query
    pattern = r"Is\s+(\w+)\s+the\s+father\s+of\s+(\w+)"
    match = re.search(pattern, message)
    
    if match: 
        # Extract names from the message
        father = match.group(1)
        child = match.group(2)
        
        # Query the Prolog knowledge base
        result = list(prolog.query(f"father('{father}', '{child}')"))
        
        # Return appropriate response based on the query result
        if result:
            print(f"Yes, {father} is the father of {child}.") 
        else:
            print(f"No, {father} is not the father of {child}.")
          
        return True
    
    return False


def process_mother_relationship(message):
    # Regular expression to extract mother relationships
    pattern = r"(\w+)\s+is\s+the\s+mother\s+of\s+(\w+)"
    match = re.search(pattern, message)
    
    if match:
        # Extract names from the message
        mother = match.group(1)
        child = match.group(2)
        
        existing_mother = list(prolog.query(f"mother(Mother, '{child}')"))
        if existing_mother:
            # If an existing mother is found, return a message and skip assertion
            current_mother = existing_mother[0]["Mother"]  
            print(f"{child} already has a mother: {current_mother}.\n")
            return True

        # Assert the fact into the Prolog database
        assert_fact(f"mother('{mother}', '{child}')")
        assert_fact(f"parent('{mother}', '{child}')")
        assert_fact(f"female('{mother}')")
        
        print(f"OK! I learned that {mother} is a parent(mother) of {child}.\n")

        siblings = list(prolog.query(f"mother('{mother}', Sibling), Sibling \\= '{child}'"))
        
        for sibling in siblings:
            sibling_name = sibling["Sibling"]
            assert_fact(f"siblings('{child}', '{sibling_name}')")
            assert_fact(f"siblings('{sibling_name}', '{child}')")
           
        
 
        siblings = list(prolog.query(f"siblings('{child}', Sibling)"))
        
        for sibling in siblings:
            sibling_name = sibling["Sibling"]
            if sibling_name != child:
                if not list(prolog.query(f"parent('{mother}', '{sibling_name}')")):
                    assert_fact(f"parent('{mother}', '{sibling_name}')")
        return True
    
    return False

def process_mother_query(message):
    # Regular expression to extract the mother and child from the query
    pattern = r"Is\s+(\w+)\s+the\s+mother\s+of\s+(\w+)"
    match = re.search(pattern, message)
    
    if match: 
        # Extract names from the message
        mother = match.group(1)
        child = match.group(2)
        
        # Query the Prolog knowledge base
        result = list(prolog.query(f"mother('{mother}', '{child}')"))
        
        # Return appropriate response based on the query result
        if result:
            print(f"Yes, {mother} is the mother of {child}.") 
        else:
            print(f"No, {mother} is not the mother of {child}.")
          
        return True
    
    return False

def process_parent_relationship(message):
    pattern = r"(\w+)\s+is\s+a\s+child\s+of\s+(\w+)"
    match = re.search(pattern, message)
    
    if match:

        child = match.group(1)
        parent = match.group(2)

        existing_parents = list(prolog.query(f"parent(Parent, '{child}')"))
        parent_counter = len(existing_parents)


        # Check if the child already has 2 parents
        if parent_counter >= 2:
            print(f"{child} already has 2 parents. Cannot add {parent} as another parent.\n")
            return True

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
        
        
        
        grandfathers = list(prolog.query(f"grandfather(Grandfather, '{child}')"))
        
        for grandfather in grandfathers:
            grandfather_name = grandfather["Grandfather"]
            assert_fact(f"parent('{grandfather_name}', '{parent}')")
                   
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

def process_sister_relationship(message):
    
    pattern = r"(\w+)\s+is\s+a\s+sister\s+of\s+(\w+)"
    match = re.search(pattern, message)
    
    if match:
        name1 = match.group(1)
        name2 = match.group(2)
        
        if name1 != name2:
            
            assert_fact(f"sister('{name1}', '{name2}')")
            assert_fact(f"female('{name1}')")
            print(f"OK! I learned that {name1} is a sister of {name2}.\n")
            
            
            if not list(prolog.query(f"siblings('{name1}', '{name2}')")):
                assert_fact(f"siblings('{name1}', '{name2}')")
            if not list(prolog.query(f"siblings('{name2}', '{name1}')")):
                assert_fact(f"siblings('{name2}', '{name1}')")
            
            # We wil get a list of the siblings of name2 and put them in a list
            siblings_of_name2 = list(prolog.query(f"siblings('{name2}', Sibling), Sibling \\= '{name2}'"))
            
            
            # Process for assigning name1 as a sibling and sister to the siblings of name2
            # We will get the siblings from the list one by one
            # We assign name1 as a sibling to sibling
            # We assign sibling as a sibling to name1
            # We assign name1 as a sister to sibling
            for sibling in siblings_of_name2:
                sibling_name = sibling["Sibling"]
                if sibling_name != name1:
                    if not list(prolog.query(f"siblings('{name1}', '{sibling_name}')")):
                        assert_fact(f"siblings('{name1}', '{sibling_name}')")
                    if not list(prolog.query(f"siblings('{sibling_name}', '{name1}')")):
                        assert_fact(f"siblings('{sibling_name}', '{name1}')")
                    if not list(prolog.query(f"sister('{name1}', '{sibling_name}')")):
                        assert_fact(f"sister('{name1}', '{sibling_name}')")
                    
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

def process_sister_query(message):
    
    pattern = r"Is\s+(\w+)\s+a\s+sister\s+of\s+(\w+)\?"
    match = re.search(pattern, message)
    
    if match:
        name1 = match.group(1)
        name2 = match.group(2)
        result = list(prolog.query(f"siblings('{name1}', '{name2}')"))
        
        
        
        if result:
            print(f"Yes, {name1} is a sister of {name2}.\n")
        else:
            print(f"No, {name1} is not a sister of {name2}.\n")
            
            
        return True
    
    
    return False
    

def process_brother_relationship(message):
    pattern = r"(\w+)\s+is\s+a\s+brother\s+of\s+(\w+)"
    match = re.search(pattern, message)
    
    if match:
        name1 = match.group(1)
        name2 = match.group(2)
        
        if name1 != name2:
            
            assert_fact(f"brother('{name1}', '{name2}')")
            assert_fact(f"male('{name1}')")
            print(f"OK! I learned that {name1} is a brother of {name2}.\n")
            
            
            if not list(prolog.query(f"siblings('{name1}', '{name2}')")):
                assert_fact(f"siblings('{name1}', '{name2}')")
            if not list(prolog.query(f"siblings('{name2}', '{name1}')")):
                assert_fact(f"siblings('{name2}', '{name1}')")
            
            # We wil get a list of the siblings of name2 and put them in a list
            siblings_of_name2 = list(prolog.query(f"siblings('{name2}', Sibling), Sibling \\= '{name2}'"))
            
            
            # Process for assigning name1 as a sibling and brother to the siblings of name2
            # We will get the siblings from the list one by one
            # We assign name1 as a sibling to sibling
            # We assign sibling as a sibling to name1
            # We assign name1 as a brother to sibling
            for sibling in siblings_of_name2:
                sibling_name = sibling["Sibling"]
                if sibling_name != name1:
                    if not list(prolog.query(f"siblings('{name1}', '{sibling_name}')")):
                        assert_fact(f"siblings('{name1}', '{sibling_name}')")
                    if not list(prolog.query(f"siblings('{sibling_name}', '{name1}')")):
                        assert_fact(f"siblings('{sibling_name}', '{name1}')")
                    if not list(prolog.query(f"sister('{name1}', '{sibling_name}')")):
                        assert_fact(f"sister('{name1}', '{sibling_name}')")
                    
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



def process_brother_query(message):
    
    pattern = r"Is\s+(\w+)\s+a\s+brother\s+of\s+(\w+)\?"
    match = re.search(pattern, message)
    
    if match:
        name1 = match.group(1)
        name2 = match.group(2)
        result = list(prolog.query(f"siblings('{name1}', '{name2}')"))
        
        
        if result:
            print(f"Yes, {name1} is a brother of {name2}.\n")
        else:
            print(f"No, {name1} is not a brother of {name2}.\n")
            
            
        return True
    
    
    return False



def process_children_list_query(message):   
    pattern = r"Who\s+are\s+the\s+children\s+of\s+(\w+)\?"
    match = re.search(pattern, message)
    
    if match:
        name1 = match.group(1)
        children = list(prolog.query(f"parent('{name1}', Child), Child \\= '{name1}'"))
        
        
        if children:
            
            children_names = ', '.join(children["Child"] for children in children)
            print(children_names)
            print()    
        return True
    

    return False 

def process_sibling_list_query(message):
    
    
    pattern = r"Who\s+are\s+the\s+siblings\s+of\s+(\w+)\?"
    match = re.search(pattern, message)
    
    if match:
        name1 = match.group(1)
        siblings = list(prolog.query(f"siblings('{name1}', Sibling), Sibling \\= '{name1}'"))
        
        
        if siblings:
            
            sibling_names = ', '.join(sibling["Sibling"] for sibling in siblings)
            print(sibling_names)
            print()    
        return True
    

    return False   
        

def process_sister_list_query(message):
    pattern = r"Who\s+are\s+the\s+sisters\s+of\s+(\w+)\?"
    match = re.search(pattern, message)
    
    if match:
        name1 = match.group(1)
        sisters = list(prolog.query(f"siblings('{name1}', Sibling), female(Sibling)"))
        
        if sisters:
            sisters_names = ', '.join(sister["Sibling"] for sister in sisters)
            print(sisters_names)
            print()
        else:
            print(f"{name1} has no sisters.")
        
        return True
    
    return False


def process_brother_list_query(message):
    pattern = r"Who\s+are\s+the\s+brothers\s+of\s+(\w+)\?"
    match = re.search(pattern, message)
    
    if match:
        name1 = match.group(1)
        brothers = list(prolog.query(f"siblings('{name1}', Sibling), male(Sibling)"))
        
        if brothers:
            brothers_names = ', '.join(brothers["Sibling"] for brothers in brothers)
            print(brothers_names)
            print()
        else:
            print(f"{name1} has no sisters.")
        
        return True
    
    return False

def process_son_relationship(message):
    pattern = r"(\w+)\s+is\s+a\s+son\s+of\s+(\w+)"
    match = re.search(pattern, message)

    if match: 
       son = match.group(1)
       parent = match.group(2)
       
       existing_parents = list(prolog.query(f"parent(Parent, '{son}')"))
       parent_counter = len(existing_parents)


        # Check if the child already has 2 parents
       if parent_counter >= 2:
            print(f"{son} already has 2 parents. Cannot add {parent} as another parent.\n")
            return True

       assert_fact(f"parent('{parent}', '{son}')")
       assert_fact(f"male('{son}')")
       print(f"OK! I learned that {son} is a son of {parent}.\n")
            
        
       siblings = list(prolog.query(f"parent('{parent}', Sibling), Sibling \\= '{son}', male({son})"))
        
       for sibling in siblings:
            sibling_name = sibling["Sibling"]
            assert_fact(f"siblings('{son}', '{sibling_name}')")
            assert_fact(f"siblings('{sibling_name}', '{son}')")
           
        
 
       siblings = list(prolog.query(f"siblings('{son}', Sibling)"))
        
       for sibling in siblings:
            sibling_name = sibling["Sibling"]
            if sibling_name != son:
                if not list(prolog.query(f"parent('{parent}', '{sibling_name}')")):
                    assert_fact(f"parent('{parent}', '{sibling_name}')")
                   
       return True
    
    return False


def process_daughter_relationship(message):
    pattern = r"(\w+)\s+is\s+a\s+daughter\s+of\s+(\w+)"
    match = re.search(pattern, message)

    if match: 
       daughter = match.group(1)
       parent = match.group(2)
    

       existing_parents = list(prolog.query(f"parent(Parent, '{daughter}')"))
       parent_counter = len(existing_parents)


        # Check if the child already has 2 parents
       if parent_counter >= 2:
            print(f"{daughter} already has 2 parents. Cannot add {parent} as another parent.\n")
            return True

        # Check if the child already has 2 parents
       if parent_counter[daughter] >= 2:
            print(f"{daughter} already has 2 parents. Cannot add {parent} as another parent.\n")
            return True

       assert_fact(f"parent('{parent}', '{daughter}')")
       assert_fact(f"male('{daughter}')")
       print(f"OK! I learned that {daughter} is a daughter of {parent}.\n")
            
        
       siblings = list(prolog.query(f"parent('{parent}', Sibling), Sibling \\= '{daughter}', male({daughter})"))
        
       for sibling in siblings:
            sibling_name = sibling["Sibling"]
            assert_fact(f"siblings('{daughter}', '{sibling_name}')")
            assert_fact(f"siblings('{sibling_name}', '{daughter}')")
           
        
 
       siblings = list(prolog.query(f"siblings('{daughter}', Sibling)"))
        
       for sibling in siblings:
            sibling_name = sibling["Sibling"]
            if sibling_name != daughter:
                if not list(prolog.query(f"parent('{parent}', '{sibling_name}')")):
                    assert_fact(f"parent('{parent}', '{sibling_name}')")
                   
       return True
    
    return False


def process_sons_list_query(message):
    pattern = r"Who\s+are\s+the\s+sons\s+of\s+(\w+)\?"
    match = re.search(pattern, message)
    
    if match:
        name1 = match.group(1)
        sons = list(prolog.query(f"parent('{name1}', Son), male(Son)"))
        
        if sons:
           sons_names = ', '.join(sons["Son"] for sons in sons)
           print(sons_names)
           print()
        else:
            print(f"{name1} has no sons.")
        
        return True
    
    return False

def process_daughters_list_query(message):
    pattern = r"Who\s+are\s+the\s+daughters\s+of\s+(\w+)\?"
    match = re.search(pattern, message)
    
    if match:
        name1 = match.group(1)
        daughters = list(prolog.query(f"Parent('{name1}', daughters), female(daughters)"))
        
        if daughters:
           daughters_names = ', '.join(daughters["daughter"] for daughters in daughters)
           print(daughters_names)
           print()
        else:
            print(f"{name1} has no daughters.")
        
        return True
    
    return False

def process_grandfather_relationship(message):
    
    pattern = r"(\w+)\s+is\s+a\s+grandfather\s+of\s+(\w+)"
    match = re.search(pattern, message)
    
    if match:
        
        grandfather = match.group(1)
        grandkid = match.group(2)
        
        # Check if the grandkid already has a grandfather
        existing_grandfathers = list(prolog.query(f"grandfather(G, '{grandkid}')"))
        
        if existing_grandfathers:
            print(f"{grandkid} already has a grandfather. Cannot add {grandfather} as another grandfather.\n")
            return True
        
        # Get the parents of the grandkid
        parents = list(prolog.query(f"parent(Parent, '{grandkid}')"))

        # Add the grandfather as a parent of the parents
        for parent in parents:
            assert_fact(f"parent('{grandfather}', '{parent['Parent']}')")
        
        # Add the grandfather as a grandfather of the grandkid
        assert_fact(f"grandfather('{grandfather}', '{grandkid}')")
        
        # Get the siblings of the grandkid
        siblings = list(prolog.query(f"siblings(Sibling, '{grandkid}')"))

        # Add the grandfather as a grandfather of the siblings
        for sibling in siblings:
            assert_fact(f"grandfather('{grandfather}', '{sibling['Sibling']}')")
        
        print(f"OK! I learned that {grandfather} is a grandfather of {grandkid}.\n")
        
        return True
    
    return False        
 
def process_grandfather_query(message):
     
     pattern = r"Is\s+(\w+)\s+a\s+grandfather\s+of\s+(\w+)\?"
     match = re.search(pattern, message)
    
     if match:
        grandfather = match.group(1)
        grandkid = match.group(2)
        result = list(prolog.query(f"grandfather('{grandfather}', '{grandkid}')"))
        
        
        if result:
            print(f"Yes, {grandfather} is a grandfather of {grandkid}.\n")
        else:
            print(f"No, {grandfather} is not a grandfather of {grandkid}.\n")
            
            
        return True
    
    
     return False


def process_grandmother_relationship(message):
    
    pattern = r"(\w+)\s+is\s+a\s+grandmother\s+of\s+(\w+)"
    match = re.search(pattern, message)
    
    if match:
        
        grandmother = match.group(1)
        grandkid = match.group(2)
        
        # Check if the grandkid already has a grandmother
        existing_grandmothers = list(prolog.query(f"grandmother(G, '{grandkid}')"))
        
        if existing_grandmothers:
            print(f"{grandkid} already has a grandmother. Cannot add {grandmother} as another grandmother.\n")
            return True
        
        # Get the parents of the grandkid
        parents = list(prolog.query(f"parent(Parent, '{grandkid}')"))

        # Add the grandfather as a parent of the parents
        for parent in parents:
            assert_fact(f"parent('{grandmother}', '{parent['Parent']}')")
        
        # Add the grandfather as a grandfather of the grandkid
        assert_fact(f"grandmother('{grandmother}', '{grandkid}')")
        
        # Get the siblings of the grandkid
        siblings = list(prolog.query(f"siblings(Sibling, '{grandkid}')"))

        # Add the grandfather as a grandfather of the siblings
        for sibling in siblings:
            assert_fact(f"grandmother('{grandmother}', '{sibling['Sibling']}')")
        
        print(f"OK! I learned that {grandmother} is a grandmother of {grandkid}.\n")
        
        return True
    
    return False

def process_grandmother_query(message):
     
     pattern = r"Is\s+(\w+)\s+a\s+grandmother\s+of\s+(\w+)\?"
     match = re.search(pattern, message)
    
     if match:
        grandmother = match.group(1)
        grandkid = match.group(2)
        result = list(prolog.query(f"grandmother('{grandmother}', '{grandkid}')"))
        
        
        if result:
            print(f"Yes, {grandmother} is a grandmother of {grandkid}.\n")
        else:
            print(f"No, {grandmother} is not a grandmother of {grandkid}.\n")
            
            
        return True
    
    
     return False

def process_WhoFather_query(message):

    pattern = r"Who\s+is\s+the\s+father\s+of\s+(\w+)\?"
    match = re.search(pattern, message)

    if match:
        child = match.group(1)
        result = list(prolog.query(f"father(Father, '{child}')"))

        if result:
            # Extracting the mother from the Prolog result
           father_name = result[0]['Father']
           print(f"{father_name} is the father of {child}.\n")
        else:
            print(f"{child} has no father.\n")
            
            
        return True
    
    return False

def process_WhoMother_query(message):

    pattern = r"Who\s+is\s+the\s+mother\s+of\s+(\w+)\?"
    match = re.search(pattern, message)

    if match:
        child = match.group(1)
        result = list(prolog.query(f"mother(Mother, '{child}')"))

        if result:
            # Extracting the mother from the Prolog result
            mother_name = result[0]['Mother']
            print(f"{mother_name} is the mother of {child}.\n")
        else:
            print(f"{child} has no mother.\n")
            
            
        return True
    
    return False

def process_IsSon_query(message):

    pattern = r"Is\s+(\w+)\s+a\s+son\s+of\s+(\w+)\?"
    match = re.search(pattern, message)

    if match:
        son = match.group(1)
        parent = match.group(2)
        result = list(prolog.query(f"parent('{parent}', '{son}'), male('{son}')"))

        if result:
            print(f"Yes, {son} is a son of {parent}.\n")
        else:
            print(f"No, {son} is not a son of {parent}.\n")
        
        return True
    
    return False

def process_IsDaughter_query(message):

    pattern = r"Is\s+(\w+)\s+a\s+son\s+of\s+(\w+)\?"
    match = re.search(pattern, message)

    if match:
        daughter = match.group(1)
        parent = match.group(2)
        result = list(prolog.query(f"parent('{parent}', '{daughter}'), female('{daughter}')"))

        if result:
            print(f"Yes, {daughter} is a son of {parent}.\n")
        else:
            print(f"No, {daughter} is not a son of {parent}.\n")
        
        return True
    
    return False

def process_IsChild_query(message):

    pattern = r"Is\s+(\w+)\s+a\s+child\s+of\s+(\w+)\?"
    match = re.search(pattern, message)

    if match:
        child = match.group(1)
        parent = match.group(2)
        result = list(prolog.query(f"parent('{parent}', '{child}'), male('{child}')"))

        if result:
            print(f"Yes, {child} is a son of {parent}.\n")
        else:
            print(f"No, {child} is not a son of {parent}.\n")
        
        return True
    
    return False


def process_WhoParents_query(message):
    # Match the query pattern
    pattern = r"Who\s+are\s+the\s+parents\s+of\s+(\w+)\?"
    match = re.search(pattern, message)
    
    if match:
        child = match.group(1)  # Extract the child's name from the query
        query = f"parent(Parent, {child})"  # Prolog query to find parents
        result = list(prolog.query(query))  # Execute the query
        
        if result:
            # Iterate over the result to extract all parents
            parents = [res['Parent'] for res in result]
            parent_list = ', '.join(parents)  # Join parent names into a string
            print(f"{parent_list} are the parents of {child}.\n")
        else:
            print(f"No parents found for {child}.\n")
        
        return True

    return False


def process_AreTheParents_query(message):
    pattern = r"Are\s+(\w+)\s+and\s+(\w+)\s+the\s+parents\s+of\s+(\w+)\?"
    match = re.search(pattern, message)
    
    if match:
        parent1 = match.group(1)  # Extract the first parent's name
        parent2 = match.group(2)  # Extract the second parent's name
        child = match.group(3)    # Extract the child's name
        
        query = f"parent(Parent, {child})"  # Prolog query to find parents
        result = list(prolog.query(query))  # Execute the query
        
        if result:
            # Extract all parents from the result
            parents = [res['Parent'] for res in result]
            
            # Check if parent1 and parent2 are in the list of parents
            is_parent1 = parent1 in parents
            is_parent2 = parent2 in parents
            
            if is_parent1 and is_parent2:
                print(f"Yes, both {parent1} and {parent2} are the parents of {child}.\n")
            elif is_parent1:
                print(f"Yes, {parent1} is a parent of {child}, but {parent2} is not.\n")
            elif is_parent2:
                print(f"Yes, {parent2} is a parent of {child}, but {parent1} is not.\n")
            else:
                print(f"No, neither {parent1} nor {parent2} is a parent of {child}.\n")
        else:
            print(f"No parents found for {child}.\n")
        
        return True

    return False

def process_uncle_relationship(message):

    pattern = r"(\w+)\s+is\s+an\s+uncle\s+of\s+(\w+)"
    match = re.search(pattern, message)

    if match:
        uncle = match.group(1)
        nibling = match.group(2)

        # Set uncle as parent's sibling
        parents = list(prolog.query(f"parent(Parent, '{nibling}')"))
        for parent in parents:
            assert_fact(f"siblings('{uncle}', '{parent['Parent']}')")

        assert_fact(f"uncle('{uncle}', '{nibling}')")

        # Set as uncle for nibling's siblings
        siblings = list(prolog.query(f"siblings(Sibling, '{nibling}')"))
        for sibling in siblings:
            assert_fact(f"uncle('{uncle}', '{sibling['Sibling']}')")
        
        print(f"OK! I learned that {uncle} is an uncle of {nibling}.\n")
        
        return True

    return False

def process_uncle_query(message):

    pattern = r"Is\s+(\w+)\s+an\s+uncle\s+of\s+(\w+)\?"
    match = re.search(pattern, message)

    if match:
        uncle = match.group(1)
        nibling = match.group(2)
        result = list(prolog.query(f"uncle('{uncle}', '{nibling}')"))
        
        
        if result:
            print(f"Yes, {uncle} is an uncle of {nibling}.\n")
        else:
            print(f"No, {uncle} is not an uncle of {nibling}.\n")
            
        return True
    
    
    return False

def process_AreTheParents_relationship(message):

    pattern = r"(\w+)\s+and\s+(\w+)\s+are\s+the\s+parents\s+of\s+(\w+)"
    match = re.search(pattern, message)

    if match:
        parent1 = match.group(1)
        parent2 = match.group(2)
        child = match.group(3)

        assert_fact(f"parent('{parent1}', '{child}')")
        assert_fact(f"parent('{parent2}', '{child}')")

        print(f"OK! I learned that {parent1} and {parent2} are parents of {child}.\n")

        return True

    return False

def process_aunt_relationship(message):

    pattern = r"(\w+)\s+is\s+an\s+aunt\s+of\s+(\w+)"    
    match = re.search(pattern, message)

    if match:
        aunt = match.group(1)
        nibling = match.group(2)
        parents = list(prolog.query(f"parent(Parent, '{nibling}')"))

        for parent in parents:
            assert_fact(f"siblings('{aunt}', '{parent['Parent']}')")
            assert_fact(f"aunt('{aunt}', '{nibling}')")

        siblings = list(prolog.query(f"siblings(Sibling, '{nibling}')"))
        for sibling in siblings:
            assert_fact(f"aunt('{aunt}', '{sibling['Sibling']}')")
            
        print(f"OK! I learned that {aunt} is an aunt of {nibling}.\n")        
        return True
    return False 

def process_aunt_query(message):
     
     pattern = r"Is\s+(\w+)\s+an\s+aunt\s+of\s+(\w+)\?"
     match = re.search(pattern, message)
    
     if match:
        aunt = match.group(1)
        nibling = match.group(2)
        result = list(prolog.query(f"aunt('{aunt}', '{nibling}')"))
        
        if result:
            print(f"Yes, {aunt} is an aunt of {nibling}.\n")
        else:
            print(f"No, {aunt} is not an aunt of {nibling}.\n")
        return True      
     return False

def main():
    
    while True:
        print("Available messages:\n")
        print("I would like to enter queries\n")
        print("I would like to enter statements\n")
        print("I would like to stop talking now\n")

        message = input("Enter your message: ").strip()

        if message == "I would like to enter queries":
            qmessage = " "
            checker = True
            while qmessage != "I would like to exit queries" and checker:
                qmessage = input("Enter your message: ").strip()
                if process_sibling_query(qmessage):
                    continue
                elif process_child_query(qmessage):
                    continue
                elif process_sister_query(qmessage):
                    continue
                elif process_brother_query(qmessage):
                    continue
                elif process_sibling_list_query(qmessage):
                    continue
                elif process_sister_list_query(qmessage):
                    continue
                elif process_brother_list_query(qmessage):
                    continue
                elif process_father_query(qmessage):
                    continue
                elif process_mother_query(qmessage):
                    continue
                elif process_sons_list_query(qmessage):
                    continue
                elif process_daughters_list_query(qmessage):
                    continue
                elif process_children_list_query(qmessage):
                    continue
                elif process_grandfather_query(qmessage):
                    continue
                elif process_grandmother_query(qmessage):
                    continue
                elif process_WhoFather_query(qmessage):
                    continue
                elif process_WhoMother_query(qmessage):
                    continue
                elif process_IsSon_query(qmessage):
                    continue
                elif process_IsDaughter_query(qmessage):
                    continue
                elif process_IsChild_query(qmessage):
                    continue
                elif process_WhoParents_query(qmessage):
                    continue
                elif process_AreTheParents_query(qmessage):
                    continue
                elif process_uncle_query(qmessage):
                    continue
                elif process_aunt_query(qmessage):
                    continue
                elif qmessage == "I would like to exit queries":
                    checker = False
                else:
                    print("Sorry, I didn't understand that. Please try again.\n")

        elif message == "I would like to enter statements":
            smessage = " "
            checker = True        
            while smessage != "I would like to exit statements" and checker:
                smessage = input("Enter your message: ").strip()
                if process_sibling_relationship(smessage):
                    continue
                elif process_parent_relationship(smessage):
                    continue
                elif process_sister_relationship(smessage):
                    continue
                elif process_brother_relationship(smessage):
                    continue
                elif process_father_relationship(smessage):
                    continue
                elif process_mother_relationship(smessage):
                    continue
                elif process_son_relationship(smessage):
                    continue
                elif process_daughter_relationship(smessage):
                    continue    
                elif process_grandfather_relationship(smessage):
                    continue
                elif process_grandmother_relationship(smessage):
                    continue
                elif process_uncle_relationship(smessage):
                    continue
                elif process_AreTheParents_relationship(smessage):
                    continue      
                elif process_aunt_relationship(smessage):
                    continue
                elif smessage == "I would like to exit statements":
                    checker = False
                else:
                    print("Sorry, I didn't understand that. Please try again.\n")
        
        elif re.search(r"I\s+would\s+like\s+to\s+stop\s+talking\s+now", message, re.IGNORECASE):
            print("Goodbye!")
            break
        else:
            print("Sorry, I didn't understand that. Please try again.\n")


if __name__ == "__main__":
    main()
