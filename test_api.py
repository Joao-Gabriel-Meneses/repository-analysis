import os
from github import Github
g = Github()
query = "repo:pallets/flask is:pr created:2021-01-01..2022-11-29"
print(g.search_issues(query).totalCount)
