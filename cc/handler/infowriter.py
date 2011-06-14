import os, os.path

from cc.handler import CCHandler

__all__ = ['InfoWriter']

CC_HANDLER = 'InfoWriter'

#
# infofile writer
#

def write_atomic(fn, data):
    """Write with rename."""
    fn2 = fn + '.new'
    f = open(fn2, 'w')
    f.write(data)
    f.close()
    os.rename(fn2, fn)

class InfoWriter(CCHandler):
    """Simply writes to files."""
    def __init__(self, hname, hcf, ccscript):
        super(InfoWriter, self).__init__(hname, hcf, ccscript)

        self.dstdir = hcf.getfile('dstdir')
        self.make_subdirs = hcf.getint('host-subdirs', 0)

    def handle_msg(self, cmsg):
        """Got message from client, send to remote CC"""

        data = cmsg.get_payload()
        mtime = data['mtime']
        host = data['hostname']
        fn = os.path.basename(data['filename'])
        # sanitize
        host = host.replace('/', '_')

        # decide destination file
        if self.make_subdirs:
            subdir = os.path.join(self.dstdir, host)
            dstfn = os.path.join(subdir, fn)
            if not os.path.isdir(subdir):
                os.mkdir(subdir)
        else:
            dstfn = os.path.join(self.dstdir, '%s--%s' % (host, fn))

        # check if file exist and is older
        try:
            st = os.stat(dstfn)
            if st.st_mtime == mtime:
                self.log.info('InfoWriter.handle_msg: %s mtime matches, skipping', dstfn)
            elif st.st_mtime > mtime:
                self.log.info('InfoWriter.handle_msg: %s mtime newer, skipping', dstfn)
        except OSError:
            pass

        # write file, apply original mtime
        self.log.debug('InfoWriter.handle_msg: writing data to %s', dstfn)
        write_atomic(dstfn, data['data'])
        os.utime(dstfn, (mtime, mtime))
