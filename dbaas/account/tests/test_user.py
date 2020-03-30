# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from django.contrib.auth.models import User

from ..admin.user import TeamListFilter, UserAdmin
from model_mommy import mommy


class UserTest(TestCase):

    DEV_NAME = "Dev_User"
    DBA_NAME = "DBA_User"
    WITHOUT_TEAM_NAME = "New_User"
    PASSWORD = "12345"

    def setUp(self):
        self.role = mommy.make_recipe('account.role')
        self.organization = mommy.make('Organization')
        self.team_dba = mommy.make_recipe(
            'account.team',
            role=self.role,
            organization=self.organization
        )
        self.team_dev = mommy.make_recipe(
            'account.team',
            role=self.role,
            organization=self.organization
        )
        self.team_ops = mommy.make_recipe(
            'account.team',
            role=self.role,
            organization=self.organization
        )
        self.team_bkp = mommy.make_recipe(
            'account.team',
            role=self.role,
            organization=self.organization
        )

        self.user_dev = User.objects.create_superuser(
            self.DEV_NAME,
            email="%s@admin.com" % self.DEV_NAME, password=self.PASSWORD
        )
        self.team_dev.users.add(self.user_dev)

        self.user_dba = User.objects.create_superuser(
            self.DBA_NAME,
            email="%s@admin.com" % self.DBA_NAME, password=self.PASSWORD
        )
        self.team_dba.users.add(self.user_dba)

        self.user_without_team = User.objects.create_superuser(
            self.WITHOUT_TEAM_NAME,
            email="%s@admin.com" % self.WITHOUT_TEAM_NAME,
            password=self.PASSWORD
        )

    def _build_team_filter(self, id=None):
        params = {}
        if id:
            params[TeamListFilter.parameter_name] = str(id)

        return TeamListFilter(None, params, User, UserAdmin)

    def _choices_in_team_filter(self):
        team_filter = self._build_team_filter()
        choices = []
        for choice in team_filter.lookup_choices:
            choices.append(choice[1])
        return choices

    def _do_team_filter(self, id=None):
        filter = self._build_team_filter(id)
        return filter.queryset(None, User.objects.all())

    def test_has_without_team_in_filter(self):
        self.assertIn("without team", self._choices_in_team_filter())

    def test_has_all_teams_in_filter(self):
        choices = self._choices_in_team_filter()
        self.assertIn(self.team_dba.name, choices)
        self.assertIn(self.team_dev.name, choices)
        self.assertIn(self.team_ops.name, choices)
        self.assertIn(self.team_bkp.name, choices)

    def test_empty_team_filter(self):
        users = self._do_team_filter()
        self.assertEqual(len(users), 3)

    def test_can_filter_by_team(self):
        users = self._do_team_filter(self.team_dba.id)
        self.assertEqual(len(users), 1)

    def test_can_filter_users_without_team(self):
        users = self._do_team_filter(-1)
        self.assertEqual(len(users), 1)
