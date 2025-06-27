# -----------------------------------------------------------------------------
# License:
# Copyright (c) 2025 Gecosistema S.r.l.
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
# Name:        main.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     18/03/2021
# -----------------------------------------------------------------------------
import click

from .utils.module_s3 import copy
from .module_args import check_args
from .utils.module_prologo import prologo, epilogo


@click.command()
# -----------------------------------------------------------------------------
# Specific options of your CLI application
# -----------------------------------------------------------------------------

# TODO: Add your specific options here

# -----------------------------------------------------------------------------
# Common options to all Gecosistema CLI applications
# -----------------------------------------------------------------------------
@click.option('--backend', type=click.STRING, required=False, default=None,
              help="The backend to use for sending back progress status updates to the backend server.")
@click.option('--jid', type=click.STRING, required=False, default=None,
              help="The job ID to use for sending back progress status updates to the backend server. If not provided, it will be generated automatically.")
@click.option('--version', is_flag=True, required=False, default=False,
              help="Show the version of the package.")
@click.option('--debug', is_flag=True, required=False, default=False,
              help="Debug mode.")
@click.option('--verbose', is_flag=True, required=False, default=False,
              help="Print some words more about what is doing.")
def main_click(**kwargs):
    """
    DPC Retriever - Command Line Interface
    """
    return main_python(**kwargs)


def main_python(
    # --- Specific options ---
    
    # --- Common options ---
    backend=None,
    jid=None,
    version=False,
    debug=False,
    verbose=False
):
    """
    main_python - main function
    """
    
    # DOC: -- Init logger + cli settings + handle version and debug ------------
    t0, jid = prologo(backend, jid, version, verbose, debug)

    # DOC: -- Arguments validation ---------------------------------------------
    kwargs = {
        'backend': backend,
        'jid': jid,
        'version': version,
        'debug': debug,
        'verbose': verbose
    }
    args = check_args(**kwargs)
    epilogo(t0, backend, jid)

    # DOC: -- Main logic. Do work here -----------------------------------------
    # TODO: your stuff here
    

    # DOC: -- Cleanup the temporary files if needed ----------------------------
    epilogo(t0, backend, jid)
    
    # DOC: -- Return the response ----------------------------------------------
    # TODO: Response will be based on the main logic
    res = {
        "statusCode": 200,
        "body": {
            "message": "Arguments are valid",
            "args": args,
        }
    }

    return res
