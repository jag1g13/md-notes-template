#!/usr/bin/env python3
"""Submit completed workblocks to the RSG-Admin API from daily notes.

Workblocks will be rejected if any have already been registered for that day.
"""
import argparse
import dataclasses
import datetime
import getpass
import pathlib
from pprint import pprint
import typing

import frontmatter
import requests


@dataclasses.dataclass
class Workblock:
    project: int
    rse: int
    start_date: str
    end_date: str
    effort_rate: float
    type: str = 'EXPENDED'

    def asdict(self) -> typing.Dict:
        return dataclasses.asdict(self)


class WorkblockSubmitter:
    def __init__(self, base_url: str, rse: str):
        self.base_url = base_url
        self.rse = rse
        self._token = self.get_token()

        self.rse_pk = self.get_pk(f'{self.base_url}/api/rses/', ldap_dn=self.rse)

    def get_token(self) -> str:
        """Get auth token from local file or request from API."""
        token_file = pathlib.Path('.token')

        if not token_file.exists():
            username = input(f'Username [{self.rse}]: ') or self.rse
            password = getpass.getpass()

            r = requests.post(f'{self.base_url}/api/get-token/', data={
                'username': username,
                'password': password,
            })

            pprint(r.text)
            r.raise_for_status()

            with token_file.open(mode='w') as f:
                f.write(r.json()['token'])
            token_file.chmod(0o600)

        return token_file.read_text()

    def submit_workblocks_from_note(self, path: pathlib.Path):
        with open(path) as f:
            data = frontmatter.load(f)

        if self.is_already_submitted(data['date']):
            raise ValueError(f'Workblocks already exist for {data["date"]}')

        # Check all projects exist with correct slug
        for project in data['projects'].keys():
            try:
                _ = self.get_pk(f'{self.base_url}/api/projects/', slug=project)

            except ValueError:
                raise ValueError(f'Project not found: {project}')

        for project, effort in data['projects'].items():
            project_pk = self.get_pk(f'{self.base_url}/api/projects/', slug=project)
            workblock = Workblock(project=project_pk,
                                  rse=self.rse_pk,
                                  start_date=data['date'],
                                  end_date=data['date'],
                                  effort_rate=effort)

            r = requests.post(f'{self.base_url}/api/workblocks/',
                              data=workblock.asdict(),
                              headers={'Authorization': f'Token {self._token}'})
            r.raise_for_status()
            pprint(r.json())

    def is_already_submitted(self, date: str) -> bool:
        r = requests.get(f'{self.base_url}/api/workblocks/',
                         params={
                             'rse': self.rse_pk,
                             'start_date': date,
                             'end_date': date,
                         },
                         headers={'Authorization': f'Token {self._token}'})
        return bool(r.json())

    def get_pk(self, url: str, **kwargs) -> int:
        """Get PK of an object selected by queryparam filters."""
        r = requests.get(url, params=kwargs, headers={'Authorization': f'Token {self._token}'})
        r.raise_for_status()

        objects = r.json()
        if not len(objects) == 1:
            pprint(objects)
            raise ValueError('Incorrect number of objects returned - expected one')

        return objects[0]['pk']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    today = str(datetime.date.today())

    parser.add_argument('-r', '--rse', type=str, required=True, metavar='username')
    parser.add_argument('-f', '--file', type=str, required=True)
    parser.add_argument('-u', '--url', type=str, default='http://localhost:8000')

    args = parser.parse_args()

    submitter = WorkblockSubmitter(args.url, args.rse)
    submitter.submit_workblocks_from_note(pathlib.Path(args.file))
