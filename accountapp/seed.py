import os
# from accountapp.models import User  



def initializer():
    # populating the database here
    
    current_filename = os.path.basename(__file__)
    current_directory = os.path.dirname(__file__)
    old_path = os.path.join(current_directory,"__init__.py")
    new_path = os.path.join(current_directory,"__init1__.py")
    print("The current script is being run from:", old_path)
    print("The current script is being run from:", new_path)
    os.rename(old_path,new_path)
    file = open(old_path,"w")
    os.remove(new_path)