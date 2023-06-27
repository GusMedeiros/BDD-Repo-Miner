import github.GithubException
from github import Github
import p_requests
from functions import language_bytes_to_percentage, get_first_line, \
    mine_feature_data, append_to_dataset

token = get_first_line("token.txt")
g = Github(token)
query = 'filename:*.feature'
repos = p_requests.search_repositories("BDD", g)
for repo in repos:
    print(f"Mining repo: {repo.full_name}")
    for attempt in range(3):
        repo_info = {
            'basic repo info': {
                'name': '',
                'description': '',
                'languages': dict(),
                'license': '',
                'topics': [],
                'created_at': {
                    'day': 0,
                    'month': 0,
                    'year': 0
                },
                'pushed_at': {
                    'day': 0,
                    'month': 0,
                    'year': 0
                }
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
                'watchers': 0,
                'forks': 0,
                'stars': 0,
                'issues': 0,
                'pull_requests': 0,

            }
        }
        basic_repo_info = repo_info['basic repo info']
        github_stats = repo_info['github stats']
        created_at = basic_repo_info['created_at']
        pushed_at = basic_repo_info['pushed_at']
        try:
            basic_repo_info['license'] = p_requests.get_repo_license(repo, g).license.spdx_id
            basic_repo_info['name'] = repo.full_name
            basic_repo_info['languages'] = language_bytes_to_percentage(p_requests.get_repo_languages(repo, g))
            basic_repo_info['topics'] = repo.topics
            basic_repo_info['description'] = repo.description
            created_at['day'] = repo.created_at.day
            created_at['month'] = repo.created_at.month
            created_at['year'] = repo.created_at.year

            pushed_at['day'] = repo.pushed_at.day
            pushed_at['month'] = repo.pushed_at.month
            pushed_at['year'] = repo.pushed_at.year

            github_stats['watchers'] = repo.subscribers_count
            github_stats['forks'] = repo.forks_count
            github_stats['stars'] = repo.stargazers_count
            github_stats['issues'] = repo.open_issues
            github_stats['pull_requests'] = p_requests.get_repo_pull_request_count(repo, github=g)
            # open_issues by default counts pull_requests, so we subtract to reflect the actual
            # issues count on the GitHub website
            github_stats['issues'] = repo.open_issues - github_stats['pull_requests']
            features = p_requests.get_repo_features(f'extension:feature repo:{repo.full_name}', g)
            mine_feature_data(features, repo_info['feature data'], g)
            append_to_dataset(repo_info)
            break
        except github.UnknownObjectException as e:
            print(f"Some object was not found, 404 error")
            print(e)
        except github.RateLimitExceededException:
            p_requests.check_limit(github=g)
            print(f"ERROR: Github api limit reached. (retrying to mine repository {repo.full_name}: attempt {attempt})")
        except Exception as e:
            print(e)
            print(f"ERROR when processing repository (retrying to mine repository {repo.full_name}: attempt {attempt})")
            append_to_dataset(repo_info, "trash.json")
