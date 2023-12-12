import time
from github import Repository, Github
import datetime


def print_limits(git: Github):
    print(f'core: {git.get_rate_limit().core.remaining}/{git.get_rate_limit().core.limit}')
    print(f'search: {git.get_rate_limit().search.remaining}/{git.get_rate_limit().search.limit}')


def _sleep(func):
    def wrapper(*args, **kwargs):
        time.sleep(1)
        return func(*args, **kwargs)

    return wrapper


def _ratelimit(func):
    def wrapper(*args, **kwargs):
        g: Github = kwargs['github'] if 'github' in kwargs else args[1]
        limit = g.get_rate_limit()
        print_limits(g)

        if limit.core.remaining <= 0:
            limit = g.get_rate_limit()
            seconds = (limit.core.reset - datetime.datetime.now()).total_seconds()
            print(f'Core rate limit reached. Waiting {seconds}s')
            _sleep(seconds)
            return func(*args, **kwargs)

        limit = g.get_rate_limit()
        if limit.search.remaining <= 0:
            seconds = (limit.search.reset - datetime.datetime.now()).total_seconds()
            print(f'Search rate limit reached. Waiting {seconds}s')
            _sleep(seconds)
        return func(*args, **kwargs)

    return wrapper


@_ratelimit
@_sleep
def get_repo_license(repo: Repository, github: Github):
    return repo.get_license()


@_ratelimit
@_sleep
def get_repo_languages(repo: Repository, github: Github):
    return repo.get_languages()


@_ratelimit
@_sleep
def get_repo_features(query: str, github: Github):
    return github.search_code(query)


@_ratelimit
@_sleep
def search_repositories(query: str, github: Github):
    return github.search_repositories(query, 'stars', 'desc')


@_ratelimit
def check_limit(null=None, github: Github = None):
    return


@_ratelimit
@_sleep
def get_repo_commit_count(repo: Repository, github: Github):
    return repo.get_commits().totalCount


@_ratelimit
@_sleep
def get_repo_pull_request_count(repo: Repository, github: Github):
    return repo.get_pulls().totalCount


def _calculate_average_commit_interval(commits_list):
    try:
        commit_times = [commit.commit.author.date.timestamp() for commit in commits_list]
        commit_times.sort()
        time_diffs = [(commit_times[i + 1] - commit_times[i]) for i in range(len(commit_times) - 1)]
        average_commit_time = sum(time_diffs) / len(time_diffs)
        print(
            f"é igual?{average_commit_time}=={_calculate_average_commit_interval_test(commits_list)} {average_commit_time == _calculate_average_commit_interval_test(commits_list)}")
        return average_commit_time
    except Exception as e:
        raise (e)
        return None


def _calculate_average_commit_interval_test(commits_list):
    try:
        commit_times = [commit.commit.author.date.timestamp() for commit in commits_list]
        commit_times.sort()
        average_commit_time = (commit_times[-1] - commit_times[0]) / (len(commit_times) - 1)
        return average_commit_time
    except Exception as e:
        raise (e)
        return None


@_ratelimit
@_sleep
def get_average_commit_interval(repo: Repository, github: Github):
    return _calculate_average_commit_interval(repo.get_commits())


@_ratelimit
@_sleep
def get_branches(repo: Repository, github: Github):
    return repo.get_branches()


@_ratelimit
@_sleep
def get_average_issue_closing_time(repo: Repository, github: Github, labels=None):
    if labels is None:
        issues = repo.get_issues(state="closed")
    else:
        issues = repo.get_issues(state="closed", labels=labels)
    summatory = 0
    for issue in issues:
        issue_life = issue.closed_at - issue.created_at
        summatory += issue_life.total_seconds()
    issues_totalCount = issues.totalCount
    if issues_totalCount == 0:
        return None
    return summatory / issues_totalCount


@_ratelimit
@_sleep
def get_contributor_count(repo: Repository, github: Github):
    return repo.get_contributors().totalCount


@_ratelimit
@_sleep
def get_bug_info(repo: Repository, github: Github):
    """
    :param repo:
    :param github:
    :return: total_closed_bugs, total_open_bugs, average_closing_time
    """
    open_issues = repo.get_issues(labels={"bug"}, state="open")
    closed_issues = repo.get_issues(labels={"bug"}, state="closed")
    closed_totalCount = closed_issues.totalCount
    if closed_totalCount != 0:
        proportion = 1 / closed_totalCount
    else:
        proportion = 1
    average_closing_time = 0
    for issue in closed_issues:
        average_closing_time += (issue.closed_at - issue.created_at).total_seconds() * proportion
    return closed_totalCount, open_issues.totalCount, average_closing_time
