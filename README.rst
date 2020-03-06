ui-classes
#########

.. code:: man

   Usage: ui-classes [OPTIONS] COMMAND [ARGS]...

     ui-classes command-line manager

   Options:
     --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
     --token TEXT
     --help                          Show this message and exit.

   Commands:
     cancel     clean unavailable transfers
     clean      clean unavailable transfers
     delete     delete files
     download   list files
     files      list files
     transfers  list transfers
     version    prints the version to the STDOUT


Authentication
==============


.. code:: bash

   # export for as environment variable
   export PUTIO_CTL_TOKEN="YOUR_API_TOKEN"

   # or pass option every time
   ui-classes --token='YOURTOKEN' <command>


Commands
========


List Transfers
--------------

.. code:: bash

   ui-classes transfers


Filter by field
...............

.. code:: bash

   ui-classes transfers -f 'status=DOWNLOADING'


Clean transfers without 100% availability
-----------------------------------------

.. code:: bash

   ui-classes clean


List Files
----------

Requires parent id to be passed, use ``0`` for root and ``all`` for all files matching filters (if any)

.. code:: bash

   ui-classes files 0  # root folders

   ui-classes files all # all files

   ui-classes files all -f 'file_type=VIDEO'  # all video files


Get download links
------------------

Accepts multiple ids

.. code:: bash

   ui-classes download $(ui-classes files all -f file_type=VIDEO -f 'name=*Californication*' --only=id)


Delete files
------------

all files containing "XXX" in the name

.. code:: bash

   ui-classes delete $(ui-classes files all -f file_type=VIDEO -f 'name=*XXX*' --only=id)

Cancel specific transfers
-------------------------

.. code:: bash

   ui-classes cancel 11222233 99887766  55446663


Cancel all transfers
--------------------

.. code:: bash

   ui-classes cancel all
