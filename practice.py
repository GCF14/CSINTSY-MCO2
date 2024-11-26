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
        result = list(prolog.query(f"parent('{father}', '{child}'), father('{father}', '{child}'), male('{father}')"))
        
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
        result = list(prolog.query(f"parent('{mother}', '{child}'), mother('{mother}', '{child}'), female('{mother}')"))
        
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

        # Check if the child already has 2 parents
       if parent_counter[son] >= 2:
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
        elif process_sister_relationship(message):
            continue
        elif process_sister_query(message):
            continue
        elif process_brother_relationship(message):
            continue
        elif process_brother_query(message):
            continue
        elif process_sibling_list_query(message):
            continue
        elif process_sister_list_query(message):
            continue
        elif process_brother_list_query(message):
            continue
        elif process_father_query(message):
            continue
        elif process_father_relationship(message):
            continue
        elif process_mother_relationship(message):
            continue
        elif process_mother_query(message):
            continue
        elif process_son_relationship(message):
            continue
        elif process_daughter_relationship(message):
            continue
        elif process_sons_list_query(message):
            continue
        elif process_daughters_list_query(message):
            continue
        elif process_children_list_query(message):
            continue
        elif process_grandfather_relationship(message):
            continue
        elif process_grandfather_query(message):
            continue
        elif re.search(r"I\s+would\s+like\s+to\s+stop\s+talking\s+now", message, re.IGNORECASE):
            print("Goodbye!")
            break
        else:
            print("Sorry, I didn't understand that. Please try again.\n")


if __name__ == "__main__":
    main()