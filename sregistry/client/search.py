'''

Copyright (C) 2017-2018 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

from sregistry.logger import bot

def main(args,parser,subparser):

    from sregistry.main import get_client

    for query in args.query:
        if query in ['','*']:
            query = None

        try:
            cli = get_client(query, args.quiet)
            cli.announce(args.command)
            cli.search(query=query, args=args)
        except NotImplementedError:
            bot.info('Search is not available for this endpoint.')
