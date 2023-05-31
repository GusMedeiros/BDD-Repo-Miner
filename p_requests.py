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
