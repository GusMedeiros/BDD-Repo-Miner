import base64
import os
import re
import time

from github import Github

import csv

import json


def append_to_dataset(data_dict):
    file_name = "data.json"  # Fixed file name

    # Load existing data from the file
    try:
        with open(file_name, 'r') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = []

    # Append the new dictionary to the existing data
    existing_data.append(data_dict)

    # Write the updated data back to the file
    with open(file_name, 'w') as file:
        json.dump(existing_data, file, indent=4)


def count_start(string, substring):
    count = 0

    for line in string.splitlines():
        stripped_line = line.strip()
        if stripped_line.startswith(substring):
            count += 1

    return count

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


token = 'mytoken'
g = Github(token)
query = 'filename:*.feature'
repos = g.search_repositories("BDD")
for repo in repos:
    features = g.search_code(query=f'extension:feature repo:{repo.full_name}')
    repo_info = {
        'basic repo info': {
            'name': repo.full_name,
            'languages': repo.get_languages(),
            'license': repo.get_license().license.spdx_id,
        },
        'feature data': {
            'total_features': 0,
            'scenario_keywords': 0,
            'scenario_outline_keywords': 0,
            'examples_keywords': 0,
            'example_keywords': 0,
            'total_examples_tables': 0,
        }
    }
    for f in features:
        feature_data = repo_info['feature data']
        f_string = base64.b64decode(f.content).decode('utf-8').lower()
        f_string_minus_comments = remove_comments(f_string)
        feature_data['total_features'] += 1
        feature_data['scenario_keywords'] += count_start(f_string_minus_comments, "scenario:")
        feature_data['scenario_outline_keywords'] += count_start(f_string_minus_comments, "scenario outline:")
        feature_data['examples_keywords'] += count_start(f_string_minus_comments, "examples:")
        feature_data['example_keywords'] += count_start(f_string_minus_comments, "example:")
        feature_data['total_examples_tables'] += count_examples_tables(f_string_minus_comments)
    append_to_dataset(repo_info)

