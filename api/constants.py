import re

pat_entry_id = re.compile(r'^(ModAction_)?(?P<entry_id>[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12})$')
pat_user = re.compile(r'^(?:/?u/)?(?P<username>[a-zA-Z0-9_]{3,20})$')

limit_allowed = [*range(1, 10), 20, 50, 100]
