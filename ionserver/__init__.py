import os
name = "ionserver"

os.environ['ISCCSHFROMMODULE'] = "True"
from .ccshd import *
from .Registrar import Registrar

