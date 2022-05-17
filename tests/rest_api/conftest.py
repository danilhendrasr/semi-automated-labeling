# Copyright (C) 2021 Intel Corporation
#
# SPDX-License-Identifier: MIT
from subprocess import run, CalledProcessError
import pytest
import json
import os.path as osp
from .utils.config import ASSETS_DIR

CVAT_DB_DIR = osp.join(ASSETS_DIR, 'cvat_db')

def _run(command):
    try:
        run(command.split(), check=True) #nosec
    except CalledProcessError:
        pytest.exit(f'Command failed: {command}. Add `-s` option to see more details')

def restore_data_volume():
    _run(f"docker container cp {osp.join(ASSETS_DIR, 'cvat_db', 'cvat_data.tar.bz2')} cvat:cvat_data.tar.bz2")
    _run(f"docker exec -i cvat tar --strip 3 -xjf /cvat_data.tar.bz2 -C /home/django/data/")

def create_test_db():
    _run(f"docker container cp {osp.join(CVAT_DB_DIR, 'restore.sql')} cvat_db:restore.sql")
    _run(f"docker container cp {osp.join(CVAT_DB_DIR, 'data.json')} cvat:data.json")
    _run('docker exec cvat python manage.py loaddata /data.json')
    _run('docker exec cvat_db psql -U root -d postgres -v from=cvat -v to=test_db -f restore.sql')

@pytest.fixture(scope='session', autouse=True)
def init_test_db():
    restore_data_volume()
    create_test_db()

    yield

    _run('docker exec cvat_db psql -U root -d postgres -v from=test_db -v to=cvat -f restore.sql')
    _run('docker exec cvat_db dropdb test_db')

@pytest.fixture(scope='function', autouse=True)
def restore():
    _run('docker exec cvat_db psql -U root -d postgres -v from=test_db -v to=cvat -f restore.sql')

class Container:
    def __init__(self, data, key='id'):
        self.raw_data = data
        self.map_data = { obj[key]: obj for obj in data }

    @property
    def raw(self):
        return self.raw_data

    @property
    def map(self):
        return self.map_data

    def __iter__(self):
        return iter(self.raw_data)

    def __len__(self):
        return len(self.raw_data)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.raw_data[key]
        return self.map_data[key]

@pytest.fixture(scope='module')
def users():
    with open(osp.join(ASSETS_DIR, 'users.json')) as f:
        return Container(json.load(f)['results'])

@pytest.fixture(scope='module')
def organizations():
    with open(osp.join(ASSETS_DIR, 'organizations.json')) as f:
        return Container(json.load(f))

@pytest.fixture(scope='module')
def memberships():
    with open(osp.join(ASSETS_DIR, 'memberships.json')) as f:
        return Container(json.load(f)['results'])

@pytest.fixture(scope='module')
def tasks():
    with open(osp.join(ASSETS_DIR, 'tasks.json')) as f:
        return Container(json.load(f)['results'])

@pytest.fixture(scope='module')
def projects():
    with open(osp.join(ASSETS_DIR, 'projects.json')) as f:
        return Container(json.load(f)['results'])

@pytest.fixture(scope='module')
def jobs():
    with open(osp.join(ASSETS_DIR, 'jobs.json')) as f:
        return Container(json.load(f)['results'])

@pytest.fixture(scope='module')
def invitations():
    with open(osp.join(ASSETS_DIR, 'invitations.json')) as f:
        return Container(json.load(f)['results'], key='key')

@pytest.fixture(scope='module')
def annotations():
    with open(osp.join(ASSETS_DIR, 'annotations.json')) as f:
        return json.load(f)

@pytest.fixture(scope='module')
def cloud_storages():
    with open(osp.join(ASSETS_DIR, 'cloudstorages.json')) as f:
        return Container(json.load(f)['results'])

@pytest.fixture(scope='module')
def issues():
    with open(osp.join(ASSETS_DIR, 'issues.json')) as f:
        return Container(json.load(f)['results'])

@pytest.fixture(scope='module')
def users_by_name(users):
    return {user['username']: user for user in users}

@pytest.fixture(scope='module')
def jobs_by_org(tasks, jobs):
    data = {}
    for job in jobs:
        data.setdefault(tasks[job['task_id']]['organization'], []).append(job)
    data[''] = data.pop(None, [])
    return data

@pytest.fixture(scope='module')
def tasks_by_org(tasks):
    data = {}
    for task in tasks:
        data.setdefault(task['organization'], []).append(task)
    data[''] = data.pop(None, [])
    return data

@pytest.fixture(scope='module')
def issues_by_org(tasks, jobs, issues):
    data = {}
    for issue in issues:
        data.setdefault(tasks[jobs[issue['job']]['task_id']]['organization'], []).append(issue)
    data[''] = data.pop(None, [])
    return data

@pytest.fixture(scope='module')
def assignee_id():
    def get_id(data):
        if data.get('assignee') is not None:
            return data['assignee']['id']
    return get_id

def ownership(func):
    def wrap(user_id, resource_id):
        if resource_id is None:
            return False
        return func(user_id, resource_id)
    return wrap

@pytest.fixture(scope='module')
def is_project_staff(projects, assignee_id):
    @ownership
    def check(user_id, pid):
        return user_id == projects[pid]['owner']['id'] or \
            user_id == assignee_id(projects[pid])
    return check

@pytest.fixture(scope='module')
def is_task_staff(tasks, is_project_staff, assignee_id):
    @ownership
    def check(user_id, tid):
        return user_id == tasks[tid]['owner']['id'] or \
            user_id == assignee_id(tasks[tid]) or \
            is_project_staff(user_id, tasks[tid]['project_id'])
    return check

@pytest.fixture(scope='module')
def is_job_staff(jobs, is_task_staff, assignee_id):
    @ownership
    def check(user_id, jid):
        return user_id == assignee_id(jobs[jid]) or \
            is_task_staff(user_id, jobs[jid]['task_id'])
    return check

@pytest.fixture(scope='module')
def is_issue_staff(issues, jobs, assignee_id):
    @ownership
    def check(user_id, issue_id):
        return user_id == issues[issue_id]['owner']['id'] or \
            user_id == assignee_id(issues[issue_id]) or \
            user_id == assignee_id(jobs[issues[issue_id]['job']])
    return check

@pytest.fixture(scope='module')
def is_issue_admin(issues, jobs, is_task_staff):
    @ownership
    def check(user_id, issue_id):
        return is_task_staff(user_id, jobs[issues[issue_id]['job']]['task_id'])
    return check

@pytest.fixture(scope='module')
def find_users(test_db):
    def find(**kwargs):
        assert len(kwargs) > 0
        assert any(kwargs.values())

        data = test_db
        kwargs = dict(filter(lambda a: a[1] is not None, kwargs.items()))
        for field, value in kwargs.items():
            if field.startswith('exclude_'):
                field = field.split('_', maxsplit=1)[1]
                exclude_rows = set(v['id'] for v in
                    filter(lambda a: a[field] == value, test_db))
                data = list(filter(lambda a: a['id'] not in exclude_rows, data))
            else:
                data = list(filter(lambda a: a[field] == value, data))

        return data
    return find

@pytest.fixture(scope='module')
def test_db(users, users_by_name, memberships):
    data = []
    fields = ['username', 'id', 'privilege', 'role', 'org', 'membership_id']
    def add_row(**kwargs):
        data.append({field: kwargs.get(field) for field in fields})

    for user in users:
        for group in user['groups']:
            add_row(username=user['username'], id=user['id'], privilege=group)

    for membership in memberships:
        username = membership['user']['username']
        for group in users_by_name[username]['groups']:
            add_row(username=username, role=membership['role'], privilege=group,
                id=membership['user']['id'], org=membership['organization'],
                membership_id=membership['id'])

    return data

@pytest.fixture(scope='module')
def org_staff(memberships):
    def find(org_id):
        if org_id in ['', None]:
            return set()
        else:
            return set(m['user']['id'] for m in memberships
                if m['role'] in ['maintainer', 'owner'] and m['user'] != None
                    and m['organization'] == org_id)
    return find

@pytest.fixture(scope='module')
def is_org_member(memberships):
    def check(user_id, org_id):
        if org_id in ['', None]:
            return True
        else:
            return user_id in set(m['user']['id'] for m in memberships
                if m['user'] != None and m['organization'] == org_id)
    return check

@pytest.fixture(scope='module')
def find_job_staff_user(is_job_staff):
    def find(jobs, users, is_staff):
        for job in jobs:
            for user in users:
                if is_staff == is_job_staff(user['id'], job['id']):
                    return user['username'], job['id']
        return None, None
    return find

@pytest.fixture(scope='module')
def find_task_staff_user(is_task_staff):
    def find(tasks, users, is_staff):
        for task in tasks:
            for user in users:
                if is_staff == is_task_staff(user['id'], task['id']):
                    return user['username'], task['id']
        return None, None
    return find

@pytest.fixture(scope='module')
def find_issue_staff_user(is_issue_staff, is_issue_admin):
    def find(issues, users, is_staff, is_admin):
        for issue in issues:
            for user in users:
                i_admin, i_staff = is_issue_admin(user['id'], issue['id']), is_issue_staff(user['id'], issue['id'])
                if (is_admin is None and (i_staff or i_admin) == is_staff) \
                    or (is_admin == i_admin and is_staff == i_staff):
                    return user['username'], issue['id']
        return None, None
    return find

@pytest.fixture(scope='module')
def filter_jobs_with_shapes(annotations):
    def find(jobs):
        return list(filter(lambda j: annotations['job'][str(j['id'])]['shapes'], jobs))
    return find

@pytest.fixture(scope='module')
def filter_tasks_with_shapes(annotations):
    def find(tasks):
        return list(filter(lambda t: annotations['task'][str(t['id'])]['shapes'], tasks))
    return find
