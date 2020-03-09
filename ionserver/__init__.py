import os
name = "ionserver"

os.environ['ISCCSHFROMMODULE'] = "True"
from .iond import *
from .Registrar import Registrar

