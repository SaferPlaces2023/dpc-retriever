# -------------------------------------------------------------------------------
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
# Name:        filesystem.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     16/12/2019
# -------------------------------------------------------------------------------

import os
import hashlib
import tempfile
import datetime

from dpc_retriever.cli.module_log import Logger


_PACKAGE_TEMP_DIR = os.path.join(tempfile.gettempdir(), 'dpc-retriever')
if not os.path.exists(_PACKAGE_TEMP_DIR):
    os.makedirs(_PACKAGE_TEMP_DIR, exist_ok=True)


# DOC: Garbage collection of temp-files
_GARBAGE_TEMP_FILES = set()

def collect_garbage_temp_file(file_path):
    """
    Collects a temporary file for garbage collection.
    """
    _GARBAGE_TEMP_FILES.add(file_path)
    if file_path.endswith('.shp'):
        add_ext = ['.shx', '.dbf', '.prj', '.cpg']
        for ext in add_ext:
            _GARBAGE_TEMP_FILES.add(file_path.replace('.shp', ext))



def now():
    """
    now
    """
    return datetime.datetime.now()


def total_seconds_from(t):
    """
    total_seconds_from
    """
    return (datetime.datetime.now() - t).total_seconds()


def normpath(pathname):
    """
    normpath
    """
    if not pathname:
        return ""
    return os.path.normpath(pathname.replace("\\", "/")).replace("\\", "/")


def juststem(pathname):
    """
    juststem
    """
    pathname = os.path.basename(pathname)
    (root, _) = os.path.splitext(pathname)
    return root


def justpath(pathname, n=1):
    """
    justpath
    """
    for _ in range(n):
        pathname, _ = os.path.split(normpath(pathname))
    if pathname == "":
        return "."
    return normpath(pathname)


def justfname(pathname):
    """
    justfname - returns the basename
    """
    return normpath(os.path.basename(normpath(pathname)))


def justext(pathname):
    """
    justext
    """
    pathname = os.path.basename(normpath(pathname))
    (_, ext) = os.path.splitext(pathname)
    return ext.lstrip(".")


def forceext(pathname, newext):
    """
    forceext
    """
    (root, _) = os.path.splitext(normpath(pathname))
    newext = newext.lstrip(".")
    pathname = root + ("." + newext if len(newext.strip()) > 0 else "")
    return normpath(pathname)


def isfile(pathname):
    """
    isfile
    """
    return pathname and isinstance(pathname, str) and os.path.isfile(pathname)


def israster(pathname):
    """
    israster
    """
    
    raster_extensions = [".tif", ".tiff", ".geotiff"]
    return isfile(pathname) and any(pathname.lower().endswith(ext) for ext in raster_extensions)


def isvector(pathname):
    """
    isvector
    """
    
    vector_extensions = [".json", ".geojson", ".shp"]
    return isfile(pathname) and any(pathname.lower().endswith(ext) for ext in vector_extensions)


def iss3(filename):
    """
    iss3
    """
    return filename and (filename.startswith("s3://") or filename.startswith("/vsis3/"))


def mkdirs(pathname):
    """
    mkdirs - create a folder
    """
    try:
        if os.path.isfile(pathname):
            pathname = justpath(pathname)
        os.makedirs(pathname)
    except:
        pass
    return os.path.isdir(pathname)


def tempdir(name=""):
    """
    tempdir
    :return: a temporary directory
    """
    foldername = normpath(tempfile.gettempdir() + "/" + name)
    os.makedirs(foldername, exist_ok=True)
    return foldername


def tempfilename(prefix="", suffix="", include_timestamp=True, add_to_garbage_collection=True):
    """
    return a temporary filename
    """
    timestamp = f"%Y%m%d%H%M%S%f" if include_timestamp else ""
    temp_filepath = normpath(_PACKAGE_TEMP_DIR + "/" + datetime.datetime.strftime(now(), f"{prefix}{timestamp}{suffix}"))
    if add_to_garbage_collection:
        collect_garbage_temp_file(temp_filepath)
    return temp_filepath

def clean_temp_files(from_garbage_collection=True):
    """
    Cleans up temporary files collected for garbage collection.
    """
    if from_garbage_collection:
        n_files = len(_GARBAGE_TEMP_FILES)
        for fp in _GARBAGE_TEMP_FILES:
            try:
                if os.path.exists(fp):
                    os.remove(fp)
            except Exception as e:
                n_files -= 1
                Logger.error(f"Error removing temporary file {fp}: {e}")
        _GARBAGE_TEMP_FILES.clear()
        Logger.debug(f"Removed {n_files} temporary files from garbage collection.")
    else:
        tempfile_dir = tempfile.gettempdir()
        tmp_fps = [os.path.join(tempfile_dir, f) for f in os.listdir(tempfile_dir) if os.path.isfile(os.path.join(tempfile_dir, f))]
        n_files = len(tmp_fps)
        for fp in tmp_fps:
            try:
                if os.path.exists(fp):
                    os.remove(fp)
            except Exception as e:
                n_files -= 1
                Logger.error(f"Error removing temporary file {fp}: {e}")
        Logger.debug(f"Removed {n_files} temporary files from module temp directory: {tempfile_dir}.")


def md5sum(filename):
    """
    md5sum - returns themd5 of the file
    """
    res = ""
    with open(filename, mode='rb') as stream:
        digestor = hashlib.md5()
        while True:
            buf = stream.read(4096)
            if not buf:
                break
            digestor.update(buf)
        res = digestor.hexdigest()
        return res


def md5text(text):
    """
    md5text - Returns the md5 of the text
    """
    if text is not None:
        digestor = hashlib.md5()
        if isinstance(text, (bytes, bytearray)):
            digestor.update(text)
        else:
            digestor.update(text.encode("utf-8"))
        return digestor.hexdigest()
    return None
