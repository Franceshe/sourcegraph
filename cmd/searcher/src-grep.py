#!/usr/bin/env python

import argparse
import requests
import sys

parser = argparse.ArgumentParser(description='Text search via sourcegraph.com')
parser.add_argument('repo', type=str, metavar='REPO', help='repo to search. eg github.com/sourcegraph/go-langserver')
parser.add_argument('pattern', type=str, metavar='PATTERN', help='pattern to search for')
parser.add_argument('rev', type=str, metavar='REV', nargs='?', default='HEAD', help='the commit to search (default HEAD)')
parser.add_argument('--dev', action='store_true', help='search via localhost rather than sourcegraph.com')
parser.add_argument('-e', '--regexp', action='store_true', help='Interpret PATTERN as a regex rather than a fixed string')
parser.add_argument('-w', '--word-regexp', action='store_true', help='Only match on word boundaries')
parser.add_argument('-i', '--ignore-case', action='store_true', help='Ignore case when matching')

args = parser.parse_args()

graphql = {
    'query': '''
query($uri: String!, $pattern: String!, $rev: String!, $isRegExp: Boolean!, $isWordMatch: Boolean!, $isCaseSensitive: Boolean!) {
    root {
        repository(uri: $uri) {
            commit(rev: $rev) {
                commit {
                    textSearch(pattern: $pattern, isRegExp: $isRegExp, isWordMatch: $isWordMatch, isCaseSensitive: $isCaseSensitive) {
                        path
                        lineMatches {
                            preview
                            lineNumber
                        }
                    }
                }
            }
        }
    }
}
    '''.strip(),
     'variables': {
	 'pattern': args.pattern,
	 'uri': args.repo,
	 'rev': args.rev,
	 'isCaseSensitive': not args.ignore_case,
	 'isRegExp': args.regexp,
	 'isWordMatch': args.word_regexp,
}}

domain = 'http://localhost:3080' if args.dev else 'https://sourcegraph.com'
r = requests.post(domain + '/.api/graphql', json=graphql)
sys.stderr.write('X-Trace: ' + r.headers['X-Trace'] + '\n')
matches = r.json()["data"]["root"]["repository"]["commit"]["commit"]["textSearch"]
for fm in matches:
    for lm in fm['lineMatches']:
	print('%s:%d:%s' % (fm['path'], lm['lineNumber'], lm['preview']))
