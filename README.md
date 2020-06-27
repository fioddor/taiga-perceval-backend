# A backend for Perceval to retrieve Taiga's data
A grimoirelab-perceval backend for the API of a Taiga service [1] that extracts information about the projects hosted in such service.
It was born as a self-standing tool, but has been extended as a basic backend of grimoirelab-perceval [2], the data collector of CHAOSS GrimoireLab Tool.

[1] https://taigaio.github.io/taiga-doc/dist/api.html
[2] https://github.com/chaoss/grimoirelab-perceval

## Deployment
As of 2020-jun-25th, the current version is compatible with the official grimoirelab/full [3] docker image (it has been used as testing environment during development).
The perceval/backends/core/taiga.py executable beelongs inside /usr/local/lib/python3.5/dist-packages/ (as /usr/local/lib/python3.5/dist-packages/perceval/backends/core/taiga.py) to be available for perceval and the test runners.

[3] https://hub.docker.com/r/grimoirelab/full
