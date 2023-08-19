import base64
import json
from github import Github

from p_requests import check_limit


def mine_feature_data(features, feature_data, github: Github):
    check_limit(github=github)
    for f in features:
        f_string = base64.b64decode(f.content).decode('utf-8').lower()
        f_string_minus_comments = remove_comments(f_string)
        feature_data['total_features'] += 1
        feature_data['scenario_keywords'] += count_start(f_string_minus_comments,
                                                         ["scenario:", "cenário", "cenario"])
        feature_data['scenario_outline_keywords'] += count_start(f_string_minus_comments, ["scenario outline:"])
        feature_data['examples_keywords'] += count_start(f_string_minus_comments, ["examples:"])
        feature_data['example_keywords'] += count_start(f_string_minus_comments, ["example:"])
        feature_data['total_examples_tables'] += count_examples_tables(f_string_minus_comments)
    return


def append_to_dataset(data_dict, file_name="data.json"):
    # Load existing data from the file
    try:
        with open(file_name, 'r') as file:
            existing_data = json.load(file)
            file.close()
    except FileNotFoundError:
        existing_data = []

    # Append the new dictionary to the existing data
    existing_data.append(data_dict)

    # Write the updated data back to the file
    with open(file_name, 'w') as file:
        json.dump(existing_data, file, indent=4)
    file.close()

def count_start(string, substrings: list):
    cont = 0
    for substring in substrings:
        cont += count_start_single_substring(string, substring)
    return cont


def count_start_single_substring(string, substring):
    count = 0

    for line in string.splitlines():
        stripped_line = line.strip()
        if stripped_line.startswith(substring):
            count += 1

    return count


def language_bytes_to_percentage(languages: dict):
    total_bytes = sum(languages.values())
    for language, byte_count in languages.items():
        languages[language] = byte_count / total_bytes
    return languages


def remove_comments(string):
    lines = string.splitlines()
    cleaned_lines = []
    in_docstring = False

    for line in lines:
        line = line.strip()

        # Check if line starts a docstring
        if line.startswith('"""') and not in_docstring:
            in_docstring = True
            continue

        # Check if line ends a docstring
        if line.endswith('"""') and in_docstring:
            in_docstring = False
            continue

        # Skip lines that are part of a docstring
        if in_docstring:
            continue

        # Check if line is a comment
        if line.startswith('#'):
            continue

        # Add non-comment, non-docstring lines to the cleaned lines
        cleaned_lines.append(line)
    cleaned_string = '\n'.join(cleaned_lines)
    return cleaned_string


def count_examples_tables(string: str):
    count = 0
    lines = string.lower().splitlines()
    in_table = False
    for line in lines:
        line = line.strip()
        if line.startswith("scenario_outline"):
            in_table = False
        elif line.startswith('examples'):
            in_table = True
            continue
        elif in_table and line.startswith("|"):
            count += 1
    return count


def get_first_line(filename):
    with open(filename, 'r') as file:
        first_line = file.readline()
        file.close()
    return first_line
