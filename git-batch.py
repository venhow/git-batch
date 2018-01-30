from git import Repo, InvalidGitRepositoryError, GitCommandError
from os import listdir
from os.path import join
import argparse


def path_to_repo(path):
    """将路径转换成Repo对象，若非Git目录，则抛出异常"""
    try:
        return Repo(path)
    except InvalidGitRepositoryError:
        return None


def not_none(obj):
    return obj is not None


def get_all_git_repos(path):
    """获取指定路径中的全部Git目录"""
    return list(filter(not_none, map(path_to_repo, map(join, [path] * len(listdir(path)), listdir(path)))))


def git_pull_repos(repos):
    """拉取到最新代码"""
    for repo in repos:
        git_pull_single_repo(repo)


def git_pull_single_repo(repo):
    """拉取到最新代码"""
    if repo.is_dirty():
        print(repo.git_dir + " 包含未提交文件，已暂存。\n")
        repo.git.stash('save')
    repo.remote().pull()


def get_branch_name(branch):
    return branch.name


def get_remote_branch_name(branch_name):
    return 'origin/' + branch_name


def git_checkout(repos, branch):
    """切换分支"""
    for repo in repos:
        print(repo.git_dir)
        remote_branch = get_remote_branch_name(branch)
        try:
            if branch in list(map(get_branch_name, repo.branches)):
                # 如果存在本地分支，则直接checkout到本地分支
                print(repo.git.checkout(branch))
            elif remote_branch in list(map(get_branch_name, repo.remotes.origin.refs)):
                # 如果存在远端分支，则追踪至远端分支
                print(repo.git.checkout(remote_branch, b=branch))
            else:
                print('Your repository does not have this branch.')
        except GitCommandError:
            print("TODO")

        print()


def parse_args(path, method, branch=''):
    """解析脚本参数"""
    repos = get_all_git_repos(path)  # 获取全部仓库
    if method == 'pull':
        """拉取最新代码"""
        git_pull_repos(repos)
    elif (method == 'checkout' or 'co') and branch != '':
        """切换到指定分支"""
        git_checkout(repos, branch)


parser = argparse.ArgumentParser(description='Git 批处理工具')
parser.add_argument('-p', '--path', help='批处理目录[必填项]', required=True)
parser.add_argument('-m', '--method', help='执行方法[必填项，可选值：pull, checkout(co)]', required=True)
parser.add_argument('-b', '--branch', help='指定target分支[选填项]', required=False)

args = parser.parse_args()

parse_args(args.path, args.method, args.branch)
