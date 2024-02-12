import os

ALLOWED_EXTENSIONS = { 'png' , 'jpg' , 'jpeg' , 'gif'}
MAX_FILE_SIZE_BYTES =  10 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.' , 1)[1].lower() in ALLOWED_EXTENSIONS



def allowed_file_size(file):
    original_position = file.tell()
    file.seek(0,os.SEEK_END)
    file_size = file.tell()
    file.seek(original_position)

    return file_size <= MAX_FILE_SIZE_BYTES    