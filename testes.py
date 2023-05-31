from github import Github

import p_requests
from functions import get_first_line


def print_limites(git: Github):
    print(f'core: {git.get_rate_limit().core.remaining}/{git.get_rate_limit().core.limit}')
    print(f'search: {git.get_rate_limit().search.remaining}/{git.get_rate_limit().search.limit}')


token = get_first_line("token.txt")
g = Github(token)
print_limites(g)
features = p_requests.get_repo_features(f'extension:feature repo:{"behave/behave"}', g)
print_limites(g)

# for f in features:
#     print_limites(g)
#     f_string = base64.b64decode(f.content).decode('utf-8').lower()
#     print(f_string)
#     time.sleep(0.5)
