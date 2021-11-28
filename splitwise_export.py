from splitwise import Splitwise
import pandas as pd
import json
import os
import wget
# import pdfkit

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, new_path, create_dir = False):
        self.new_path = os.path.expanduser(new_path)
        if not os.path.isdir(self.new_path) and create_dir:
            os.mkdir(self.new_path)

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)

def yes_or_no(question, default = None):
    while "the answer is invalid":
        if default == None:
            reply = str(input(question+' (y/n): ')).lower().strip()
        elif default == True:
            reply = str(input(question+' (Y/n): ')).lower().strip()
            if reply == '':
                return True
        elif default == False:
            reply = str(input(question+' (y/N): ')).lower().strip()
            if reply == '':
                return False
        if reply[:1] == 'y':
            return True
        if reply[:1] == 'n':
            return False

def authorize(path_to_auth = None):
    if path_to_auth == None:
        path_to_auth = 'auth.json'
    
    if os.path.isfile(path_to_auth):
        with open(path_to_auth) as json_file:
            auth = json.load(json_file)
        sObj = Splitwise(auth['consumer_key'],auth['consumer_secret'],auth['access_token'])
    else:
        print("No pre-existing authorization found. Creating new auth")
        auth = {}
        # Go to https://secure.splitwise.com/apps/new and register the app to get your consumer key and secret
        auth['consumer_key'] = input("Please enter your consumer key:\n")
        auth['consumer_secret'] = input("Please enter your consumer secret:\n")

        sObj = Splitwise(auth['consumer_key'],auth['consumer_secret'])
        url, auth['secret'] = sObj.getAuthorizeURL()
        print("Authroize via the following URL")
        print(url)

        auth['oauth_token'] = url.split("=")[1]
        auth['oauth_verifier'] = input("Please enter the oauth_verifier:\n")

        auth['access_token'] = sObj.getAccessToken(auth['oauth_token'],auth['secret'],auth['oauth_verifier'])
        print("Successfully Authorized\n")
        sObj.setAccessToken(auth['access_token'])

        save = input("Save these credentials for future use? (y/n):\n")
        if save == "y":
            with open(path_to_auth, 'w') as outfile:
                json.dump(auth, outfile, indent=4)
        print("auth.json file has been saved in the current directory. Keep this file safe.")
    
    return sObj


def get_group_expenses(sObj, group_id = None):
    if sObj == None:
        print("No Splitwise object given")
        return 0
    if group_id == None:
        groups = sObj.getGroups()
        for num,group in enumerate(groups):
            print(str(num)+": "+group.getName())
        group_num = input("Export data for which group? Enter the number here:\n")
        group_id = groups[int(group_num)].getId()

    offset = None
    limit = 999 # default limit is 20
    dated_after = None
    dated_before = None
    friendship_id = None
    updated_after = None
    updated_before = None

    group = sObj.getGroup(group_id)
    members_obj = group.getMembers()
    members = []
    for member in members_obj:
        members.append(member.getFirstName())

    expenses = sObj.getExpenses(offset,limit,group_id,friendship_id,dated_after,dated_before,updated_after,updated_before)
    return expenses, members
    
def get_user_name(user):
    if user != None:
        return user.getFirstName() + user.getLastName() if user.getLastName() else ''
    else:
        return None

def download_receipt(url, folder = None):
    if folder == None:
        folder = os.getcwd()
    try:
        with cd(folder, True):
            wget.download(url)
    except:
        pass
    else:
        pass
        

def expenses_to_excel(expenses, members, filepath = None, include_deleted = None, download_receipts = None):
    if filepath == None:
        filepath = input("Enter filename (with .xlsx extension). Leave blank for default (data_export.xlsx). File will be saved in receipts directory\n")
        if not filepath:
            filepath = 'data_export.xlsx'

    detail = []
    receipts = []
    columns = [
            'Date', 
            'Description', 
            'Category', 
            'Currency', 
            'Cost'
        ]

    for member in members:
            columns.append(member)

    for expense in expenses:
        users = expense.getUsers()
        
        data = [
            expense.getDate(), 
            expense.getDescription(), 
            expense.getCategory().getName(), 
            expense.getCurrencyCode(), 
            expense.getCost()
        ]

        for i in range(0, len(users)):
            data.append(users[i].getPaidShare())
        
        receipts.append(str(expense.getReceipt().getOriginal()))
        detail.append(data)

    df = pd.DataFrame(data=detail, columns=columns)
    df['Receipt'] = receipts

    df.to_excel(filepath + '.xlsx')
    

def authorize_by_api(path_to_auth = None):
    if path_to_auth == None:
        path_to_auth = 'auth.json'
    
    if os.path.isfile(path_to_auth):
        with open(path_to_auth) as json_file:
            auth = json.load(json_file)
        sObj = Splitwise(auth['consumer_key'],auth['consumer_secret'],api_key=auth['api_key'])
    else:
        print("No pre-existing authorization found. Creating new auth")
        auth = {}
        # Go to https://secure.splitwise.com/apps/new and register the app to get your consumer key and secret
        auth['consumer_key'] = input("Please enter your consumer key:\n")
        auth['consumer_secret'] = input("Please enter your consumer secret:\n")

        sObj = Splitwise(auth['consumer_key'],auth['consumer_secret'])
        url, auth['secret'] = sObj.getAuthorizeURL()
        print("Authroize via the following URL")
        print(url)

        auth['oauth_token'] = url.split("=")[1]
        auth['api_key'] = input("Please enter the api_key:\n")

        save = input("Save these credentials for future use? (y/n):\n")
        if save == "y":
            with open(path_to_auth, 'w') as outfile:
                json.dump(auth, outfile, indent=4)
        print("auth.json file has been saved in the current directory. Keep this file safe.")
    
    return sObj

def main():
    sObj = authorize_by_api()
    expenses = get_group_expenses(sObj)
    expenses_to_excel(expenses)

if __name__ == '__main__':
    main()
