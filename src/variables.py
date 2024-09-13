import os

from utils.env_load import load_env_file


load_env_file('../.env')

M_EL_URL = os.environ['M_EL_URL']
M_CL_URL = os.environ['M_CL_URL']
H_EL_URL = os.environ['H_EL_URL']
H_CL_URL = os.environ['H_CL_URL']
ETHERSCAN_API_KEY = os.environ['ETHERSCAN_API_KEY']
