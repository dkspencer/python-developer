import requests
import base64
import re
from concurrent.futures import ProcessPoolExecutor as Executor

output_jobs_skills = {}
count = 0

count_2 = 0
test = []

job_count = 0


def main():
    """
    Call the requests GET on the provided API url.
    :return:
    """

    global job_count

    response = requests.get('http://ciivsoft.getsandbox.com/jobs',
                            headers={"Content-Type": "application/json"})

    if response.status_code != 200:
        print('Status:', response.status_code, 'Headers:',
              response.headers, 'Error Response:', response.json())

    else:
        print("Status: 200 OK, continuing...\n")

        response_json = response.json()

        skills = get_skills()

        print("Decoding job descriptions.")

        for string in response_json.get('result'):
            job_descriptions.append(base64.b64decode(
                string).decode("utf-8").replace('\xa0', u''))
            job_count += 1

        with Executor() as executor:
            for job in job_descriptions:
                skill_frequency = {}
                data = executor.submit(parse_and_create_dict, job, skills)

                # print(data.result())

                for skill, frequency in data.result().items():
                    skill_frequency.update(
                        {
                            skill.title(): frequency
                        }
                    )

                create_output(job, skill_frequency, skills)

        print(output_jobs_skills)


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

    data = {}
    for skill in skills:
        frequency = 0
        for x in re.findall(skill, description):
            frequency += 1

        data.update({skill: frequency})

    return data


# TODO Save output to file
# TODO Percentages maybe

def calculate_percentage(get_stat, skill_frequency, skills):
    """
    Calculate the percentage of the skills.txt words found in each job description.
    :return:
    """

    if get_stat == "percentage":

        length_of_skills_list = len(skills)
        skills_not_found = 0
        skills_found = 0

        for skill, frequency in skill_frequency.items():
            if frequency == 0:
                skills_not_found += 1
            else:
                skills_found += 1
        
        a = int(length_of_skills_list) - int(skills_not_found)
        percentage = int(a / int(length_of_skills_list) * 100)

        return str(percentage) + "%"


    elif get_stat == "maximum":
        result = max(skill_frequency, key=skill_frequency.get)

        return result

    elif get_stat == "minimum":
        result = min(skill_frequency, key=skill_frequency.get)

        return result

    # print(skills_not_found)
    # print(length_of_list)
    # print(skills_found)

    # a = int(length_of_list) - int(skills_not_found)
    # percentage = int(a / int(length_of_list) * 100)

    # print(str(percentage) + "\n")

    # # print(skills_dict)
    # # print(skills)


def create_output(job, skill_frequency, skills):
    """
    Generate the dict using the first line of the job description as the parent and the skills listed as children.
    :return:
    """
    job_title = job.split('\n', 1)[0].strip()
    if "job title:" not in job_title:
        job_title = "job title: " + job_title

    output = output_jobs_skills.update(
        {
            job_title.title(): {
                "Job Description": job.replace('\n', '').replace(job_title, ''),
                "Skill Frequency": skill_frequency,
                "Statistics": {
                    "Skills Found": calculate_percentage(get_stat="percentage", skill_frequency=skill_frequency, skills=skills),
                    "Highest Frequency": calculate_percentage(get_stat="maximum", skill_frequency=skill_frequency, skills=skills),
                    "Lowest Frequency": calculate_percentage(get_stat="minimum", skill_frequency=skill_frequency, skills=skills)
                }
            }
        }
    )


if __name__ == '__main__':
    job_descriptions = []
    results = {}
    main()
