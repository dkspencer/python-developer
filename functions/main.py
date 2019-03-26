import requests
import base64
import re

output = {}
count = 0

count_2 = 0


def main():
    """
    Call the requests GET on the provided API url.
    :return:
    """

    response = requests.get('http://ciivsoft.getsandbox.com/jobs', headers={"Content-Type": "application/json"})

    if response.status_code != 200:
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())

    else:
        print("Status: 200 OK, continuing...\n")

        response_json = response.json()

        skills = get_skills()

        for string in response_json.get('result'):
            skills_dict = parse_and_create_dict(description=base64.b64decode(string), skills=skills)

            # percentage = calculate_percentage(skills_dict, skills)
            print(skills_dict)

            create_output(skills_dict)


def get_skills():
    """
    Get the skills from the skills.txt file and add to skills list.
    :return:
    """

    skills = []

    with open('../skills.txt') as skills_file:
        for skill in skills_file:
            skills.append(skill.strip().lower())

    # if item in skills list is None, ignore
    skills = [s for s in skills if s]

    return skills


def parse_and_create_dict(description, skills):
    """
    Compare the list of skills with the job descriptions and creates a list per skill per job.
    :param description:
    :param skills:
    :return:
    """

    skills_dict = {}

    for skill in skills:
        frequency = 0
        for x in re.findall(skill, description):
            frequency += 1

        skills_dict.update({skill: frequency})

    return skills_dict


# frequency of skill occurance
# percentage compared to other skills
# skill name
# multithreading/processing
# convert to json or csv - probably json to feed back into another api?

def calculate_percentage(skills_dict, skills):
    """
    Calculate the percentage of the skills.txt words found in each job description.
    :return:
    """
    length_of_list = len(skills)
    skills_not_found = 0
    skills_found = 0

    for skill in skills:
        for key, value in skills_dict.items():
            if skill == key and value == 0:
                skills_not_found += 1
            else:
                skills_found += 1

    print(skills_not_found)
    print(length_of_list)
    print(skills_found)

    a = int(length_of_list) - int(skills_not_found)
    percentage = int(a / int(length_of_list) * 100)

    print(str(percentage) + "\n")

    # print(skills_dict)
    # print(skills)


def create_output(skills_dict):
    """
    Generate the dict using the first line of the job description as the parent and the skills listed as children.
    :return:
    """
    pass
    # print(skills_dict)


main()
