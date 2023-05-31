import time

import github.GithubException
from github import Github

import p_requests
from functions import language_bytes_to_percentage, get_first_line, \
    mine_feature_data, append_to_dataset

token = get_first_line("token.txt")
g = Github(token)
query = 'filename:*.feature'
repos = p_requests.search_repositories("BDD", g)
time.sleep(1)
for repo in repos:
    print(f"Mining repo: {repo.full_name}")
    for attempt in range(3):
        repo_info = {
            'basic repo info': {
                'name': '',
                'languages': dict(),
                'license': '',
                # 'about':, about project section
                # 'summary':, chatgpt generated summary from readme and about section

            },
            'feature data': {
                'total_features': 0,
                'scenario_keywords': 0,
                'scenario_outline_keywords': 0,
                'examples_keywords': 0,
                'example_keywords': 0,
                'total_examples_tables': 0,
            },
            'github stats': {
                
            }
        }
        basic_repo_info = repo_info['basic repo info']
        try:
            basic_repo_info['license'] = p_requests.get_repo_license(repo, g).license.spdx_id

        except Exception as e:
            print(f"Error getting repo's license. Will be empty instead")
            print(e)
        try:
            basic_repo_info['name'] = repo.full_name  # not a request, no need to sleep
            basic_repo_info['languages'] = language_bytes_to_percentage(p_requests.get_repo_languages(repo, g))
            features = p_requests.get_repo_features(f'extension:feature repo:{repo.full_name}', g)
            mine_feature_data(features, repo_info['feature data'], g)
            append_to_dataset(repo_info)

            break
        except github.RateLimitExceededException:
            p_requests.check_limit(github=g)
            print(f"ERROR: Github api limit reached. (retrying to mine repository {repo.full_name}: attempt {attempt})")
        except Exception as e:
            print(e)
            print(f"ERROR when processing repository (retrying to mine repository {repo.full_name}: attempt {attempt})")
            append_to_dataset(repo_info, "trash.json")

