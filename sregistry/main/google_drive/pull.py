'''

Copyright (C) 2017-2019 Vanessa Sochat.

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

from sregistry.logger import bot, ProgressBar
from sregistry.utils import ( parse_image_name, remove_uri )
from googleapiclient.http import MediaIoBaseDownload
import os
import sys


def pull(self, images, file_name=None, save=True, **kwargs):
    '''pull an image from google drive, based on a query (uri or id)
 
    Parameters
    ==========
    images: refers to the uri given by the user to pull in the format
    <collection>/<namespace>. You should have an API that is able to 
    retrieve a container based on parsing this uri.
    file_name: the user's requested name for the file. It can 
               optionally be None if the user wants a default.
    save: if True, you should save the container to the database
          using self.add()
    
    Returns
    =======
    finished: a single container path, or list of paths
    '''

    if not isinstance(images,list):
        images = [images]

    bot.debug('Execution of PULL for %s images' %len(images))

    # If used internally we want to return a list to the user.
    finished = []
    for image in images:

        q = parse_image_name( remove_uri(image) )

        # Use container search to find the container based on uri
        bot.info('Searching for %s in drive://%s' %(q['uri'],self._base))
        matches = self._container_query(q['uri'], quiet=True)

        if len(matches) == 0:
            bot.info('No matching containers found.')
            sys.exit(0)
       
        # If the user didn't provide a file, make one based on the names
        if file_name is None:
            file_name = q['storage'].replace('/','-')

        # We give the first match, the uri should be unique and known
        image = matches[0]

        request = self._service.files().get_media(fileId=image['id'])

        with open(file_name, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            bar = None

            # Download and update the user with progress bar
            while done is False:
                status, done = downloader.next_chunk()
                response = None

                # Create bar on first call
                if bar is None:
                    total = status.total_size / (1024*1024.0)
                    bar = ProgressBar(expected_size=total,
                                      filled_char='=',
                                      hide=self.quiet)

                bar.show(status.resumable_progress / (1024*1024.0))
            

        # If the user is saving to local storage, you need to assumble the uri
        # here in the expected format <collection>/<namespace>:<tag>@<version>
        if save is True:
            image_uri = q['uri']
            if "uri" in image:
                image_uri = image['uri']

            # Update metadata with selfLink
            image['selfLink'] = downloader._uri

            container = self.add(image_path = image_file,
                                 image_uri = image_uri,
                                 metadata = image,
                                 url=downloader._uri)

            # When the container is created, this is the path to the image
            image_file = container.image

        if os.path.exists(image_file):
            bot.debug('Retrieved image file %s' %image_file)
            bot.custom(prefix="Success!", message=image_file)
            finished.append(image_file)

    if len(finished) == 1:
        finished = finished[0]
    return finished
