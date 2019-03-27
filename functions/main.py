import requests
import base64
import re
import json
import sys
import logging
from concurrent.futures import ProcessPoolExecutor as Executor

# logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
# logger = logging.getLogger('main')
# logger.setLevel(logging.INFO)

logging.basicConfig(filename='main.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)


def main():
    """
    Call the requests GET on the provided API url, decode job description, start processes per job description, parse
    and save output to file.
    :return:
    """

    response = requests.get('http://ciivsoft.getsandbox.com/jobs', headers={"Content-Type": "application/json"})

    if response.status_code != 200:
        logger.error("Status: {0}, Headers: {1}, Error Response: {2}".format(response.status_code, response.headers,
                                                                             response.json()))
        print("Error, check logs.")

    else:
        logger.info("Status: {0}, continueing...".format(response.status_code))

        # Get skills list from the skills.txt file.
        skills = get_skills()

        for string in response.json().get('result'):
            job_descriptions.append(base64.b64decode(string).decode("utf-8").replace('\xa0', u''))

        logger.info("Decoded job descriptions")

        # Start separate process for each job in job description list.
        with Executor() as executor:
            logger.info("Parsing job descriptions and extracting frequency of skills matched.")
            for job in job_descriptions:
                skill_frequency = {}
                data = executor.submit(parse_and_create_dict, job, skills)

                for skill, frequency in data.result().items():
                    skill_frequency.update({skill.title(): frequency})

                create_output(job, skill_frequency, skills)

        with open('../data.json', 'w') as output_file:
            logger.info("Saving to file")
            json.dump(output_jobs_skills, output_file)

        print("Script finished successfully.")


def get_skills():
    """
    Get the skills from the skills.txt file and add to skills list.
    :return:
    """

    skills = []

    try:
        with open('../skills.txt') as skills_file:
            for skill in skills_file:
                skills.append(skill.strip().lower())

    except FileNotFoundError:
        print("Error, check logs.")
        logger.error("skills.txt file not found, exiting script.")
        sys.exit()

    skills = [s for s in skills if s]

    logger.info("Found skills.txt file, added skills to list and empty items removed.")

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


def calculate_percentage(get_stat, skill_frequency, skills):
    """
    Calculate the percentage of the skills.txt words found in each job description and return the statistics.
    As well as the highest and lowest matching skill.

    :param get_stat:
    :param skill_frequency:
    :param skills:
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


def create_output(job, skill_frequency, skills):
    """
    Using the incomming parameters, create/update the dict with the job descriptions, skill frequencies and statistics.
    As well as parse the job description for the job title to act as a dict parent.

    :param job:
    :param skill_frequency:
    :param skills:
    :return:
    """

    job_title = job.split('\n', 1)[0].strip()
    if "job title:" not in job_title:
        job_title = "job title: " + job_title

    output_jobs_skills.update(
        {
            job_title.title(): {
                "Job Description": job.replace('\n', ' ').replace(job_title, ''),
                "Skill Frequency": skill_frequency,
                "Statistics": {
                    "Skills Found": calculate_percentage(get_stat="percentage", skill_frequency=skill_frequency,
                                                         skills=skills),
                    "Highest Frequency": calculate_percentage(get_stat="maximum", skill_frequency=skill_frequency,
                                                              skills=skills),
                    "Lowest Frequency": calculate_percentage(get_stat="minimum", skill_frequency=skill_frequency,
                                                             skills=skills)
                }
            }
        }
    )


if __name__ == '__main__':
    print("Starting script.")
    job_descriptions = []
    output_jobs_skills = {}
    main()
