import requests

'''
    function: get_public_contributions
    params: username, token
    desc: This method takes in the github username to check public contributions for, as well as
          as github API token so up to 5000 requests per hour can be made (enough for demo).
          Returns total number of contributions or -1 to indicate an error has occured, likely
          an invalid username was made or a token wasn't supplied
    return: total contributions
'''


def get_public_contributions(username, token):
    response = requests.get(
        "https://api.github.com/users/"+username+"/repos?access_token="+token)
    # response = requests.get("https://api.github.com/users/"+username+"/repos")

    if response.status_code == 200:
        body = response.json()
        total_contributions = 0
        for repos in body:
            response_contributions = requests.get(
                "https://api.github.com/repos/"+repos["full_name"]+"/contributors?access_token="+token)
            # response_contributions = requests.get("https://api.github.com/repos/"+repos["full_name"])
            try:
                body_contributions = response_contributions.json()
                for contributor in body_contributions:
                    if contributor["login"] == username:
                        total_contributions += contributor["contributions"]
            except:
                pass
        return total_contributions
    return -1


'''
    function: get_public_contributions
    params: username, token
    desc: This method takes in the github username to check all contributions for, as well as
          as github API token so up to 5000 requests per hour can be made (enough for demo).
          Returns total number of contributions or -1 to indicate an error has occured, likely
          an invalid username was made or a token wasn't supplied
    return: total contributions
'''


def get_contributions(username):
    response = requests.get(
        "https://github-contributions-api.herokuapp.com/"+username+"/count")
    if response.status_code == 200:
        # print(response.content)
        body = response.json()
        total_contributions = 0
        for year in body['data']:
            for month in body['data'][year]:
                for day in body['data'][year][month]:
                    total_contributions += body['data'][year][month][day]
        return total_contributions
    return -1


result = get_contributions("Bhavik-Makwana")
print(result)
result = get_contributions("harryfallows")
print(result)

token = ""
print(get_public_contributions("harryfallows", token))
print(get_public_contributions("Bhavik-Makwana", token))
print(get_public_contributions("ilovetocode", token))
print(get_public_contributions("Newey27", token))
print(get_public_contributions("SheapMan", token))
