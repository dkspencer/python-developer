import requests
import pprint
import json
import base64
import parser
import re
import unicodedata

pp = pprint.PrettyPrinter(indent=2)
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

            print(skills_dict)


def get_skills():
    """
    Get the skills from the skills.txt file and add to skills list.
    :return:
    """

    skills = []

    with open('../skills.txt') as skills_file:
        for skill in skills_file:
            skills.append(skill.strip())  # .replace("\n", "")

    # print(filter(None, skills))

    skills = [s for s in skills if s]

    return skills


def parse_and_create_dict(description, skills):
    """
    Compare the list of skills with the job descriptions and creates a list per skill per job.
    :param description:
    :param skills:
    :return:
    """
    # print(skills)
    # print("-----------------------------------")
    # print(description + "\n\n\n")
    # print("-----------------------------------")

    skills_dict = {}
    global count
    global count_2

    # for skill in skills:
    #     frequency = 0
    #     if skill.lower() in description:
    #         count += 1
    #         frequency += 1


    words = []

    for word in description.split():
        words.append(word.strip())

    #print(words)
    for skill in skills:
        frequency = 0
        for word in words:
            if skill.lower() in word:
                frequency += 1

            skills_dict.update({skill: frequency})

    return skills_dict


# frequency of skill occurance
# percentage compared to other skills
# skill name
# multithreading/processing
# convert to json or csv - probably json to feed back into another api?

def calculate_percentage():
    """
    Calculate the percentage of the skills.txt words found in each job description.
    :return:
    """
    pass


def create_output(job_comparison_dict):
    """
    Generate the dict using the first line of the job description as the parent and the skills listed as children.
    :return:
    """

    output.update(job_comparison_dict)

    return output


main()
