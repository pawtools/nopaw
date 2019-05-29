'''
Authors: John Ossyra
Tools for executing workload. 
'''
import sys
import os
import subprocess
import shlex
import yaml

from string import Formatter

from pprint import pformat

__all__ = [
    "MongoInstance",
    "SessionMover",
    "JobBuilder",
]

get_format_fields = lambda s: [
    fname for _, fname, _, _
    in Formatter().parse(s) if fname
]

cli_args_from_dict = lambda d: ' '.join(
    [' '.join([str(k),str(v)])
    for k,v in d.items() if v is not None])

def flatten_list(l):
    '''Flatten nested lists
    down to the last turtle.
    '''
    return flatten_list(l[0]) + (
           flatten_list(l[1:]) if len(l) > 1 else []
           ) if type(l) is list else [l]


def flatten_dict(d):
    def _flatten_dict(d):
        '''Sort-of Flatten nested dict
        They come out as nested lists
        '''
      #  if isinstance(d, list):
      #      for sub_d in d:
      #          yield list(_flatten_dict(sub_d))
        if isinstance(d, dict):
            for value in d.values():
                yield list(_flatten_dict(value))
        else:
            yield d

    return list(_flatten_dict(d))


def small_proc_watch_block(command):
    '''Should only use with fast executing commands
    and manageable output size. All errors are lost.
    '''
    proc = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )

    out = proc.stdout.read()
    retval = proc.wait()

    return out, retval


# TODO replace path insert formatting with os.path.join
class MongoInstance(object):
    """A simple interface to mongod instance
    TODO describe it!
    """
    def __init__(self, dbpath, dbport=27017):
        super(MongoInstance, self).__init__()

        assert self.discover_mongod_command()
        assert isinstance(dbpath, str) # TODO check is path-like, parent dir exists
        #assert isinstance(dbport, validport) # TODO isint and betwen X and Y

        self._dblog_file = None
        self.dbpath = dbpath
        self.dbport = dbport

    def discover_mongod_command(self):
        dicover_command = "command -v mongod"
        out, retval = small_proc_watch_block(discover_command)
        if out: return True
        else:   return False

    @property
    def pid(self):
        return self.mongo_proc.pid

    @property
    def mongo_proc(self):
        return self._mongo_proc

    @property
    def dblogfile(self):
        return self._dblog_file

    def open_mongodb(self, remove_socket=False,
            remove_locks=False, create_folder=False):

        if create_folder:
            try:
                os.mkdir(self.dbpath)
                os.mkdir('{}/socket'.format(self.dbpath))
                os.mkdir('{}/db'.format(self.dbpath))

            except OSError:
                pass

        if remove_socket:
            self._remove_socket_file()

        if remove_locks:
            self._remove_lock_files()

        self._write_config_file()

        self._dblog_file = open(
            "{0}/db.log".format(self.dbpath), 'w')

        #if command -v numactl: launcher -= "numactl --interleave=all"
        launcher = "mongod --dbpath {0}/db --config {0}/db.cfg"

        self._mongo_proc = subprocess.Popen(
            shlex.split(launcher.format(self.dbpath)),
            stdout=self._dblog_file,
            stderr=self._dblog_file,
        )

    def stop_mongodb(self):

        self._mongo_proc.kill()
        self._mongo_proc.wait()
        self._dblog_file.close()
        self._remove_socket_file()
        self._remove_lock_files()

    def _remove_lock_files(self):

        mongo_lock_file = '{0}/db/mongod.lock'.format(self.dbpath)
        wt_lock_file = '{0}/db/WiredTiger.lock'.format(self.dbpath)

        if os.path.exists(mongo_lock_file):
            os.remove(mongo_lock_file)

        if os.path.exists(wt_lock_file):
            os.remove(wt_lock_file)

    def _remove_socket_file(self):

        socket_file = '{0}/socket/mongodb-{1}.sock'\
            ''.format(self.dbpath, self.dbport)

        if os.path.exists(socket_file):
            os.remove(socket_file)

    def _write_config_file(self):

        config_string = ""\
            "net:\n"\
            "   unixDomainSocket:\n"\
            "      pathPrefix: {0}/socket\n"\
            "   bindIp: localhost\n"\
            "   port:   {1}\n"\
            "".format(self.dbpath, self.dbport)
            
        config_file = "{0}/db.cfg".format(self.dbpath)

        with open(config_file,"w") as cfg:
            cfg.write(config_string)


class SessionMover(object):
    """Use this object to roll out new locations for session log files, and
    move between session locations and a starting location. Iterate to create
    new session IDs. Call `use_current` method to create folders for the
    current session and move to this working directory, then `go_back` to
    change back to the starting directory.
    
    Methods
    -------
    __init__ :: init with base path, scans for existing sessions
    use_current :: use the current session ID, ie create and go to this session folder
    use_next :: create and use the next session ID
    go_back :: move back to base path
    
    """
    _base = None
    _prefix = 'sessions'
    _first = 0
    _capture = '.log'

    def __init__(self, path):
        super(SessionMover, self).__init__()

        self._base = path
        self._path = os.path.join(path, SessionMover._prefix)
        self._currentID = None
        self._init_sessionID()

    def _init_sessionID(self):
        if not os.path.exists(self._path):
            os.mkdir(self._path)

        existing_sessions = os.listdir(self._path)
        newest = SessionMover._first

        if existing_sessions:
            for d in existing_sessions:
                try:
                    this = int(d)
                    if this > newest:
                        newest = this

                except ValueError:
                    pass

        self._currentID = newest + 1

    def capture_fwd_logs(self):
        return filter(
            lambda f: f.endswith(SessionMover._capture),
            os.listdir(self._base)
        )

    def _incr_currentID(self):
        self._currentID += 1

    def use_next(self):
        next(self)
        self.use_current()

    def use_current(self):
        os.mkdir(self.current)
        os.chdir(self.current)

    def go_back(self, capture=False):
        os.chdir(self._base)
        if capture:
            [
             os.rename(f, os.path.join(self.current, f))
             for f in self.capture_fwd_logs()
            ]

    @property
    def currentID(self):
        return "{:04}".format(self._currentID)

    @property
    def current(self):
        return os.path.join(self._path, self.currentID)

    def __iter__(self):
        return self

    def next(self):
        return self.__next__()

    def __next__(self):

        self._incr_currentID()

        if self._currentID > 9999:
            raise StopIteration

        return self.current


class JobBuilder(object):
    '''Create an LRMS job to acquire resources for a workload.
    JobBuilder reads configuration from a yaml file. Two top-level
    fields are required: "job" and "task". Options for each are
    built into the actual LRMS job.
    '''
    _live_ = True
    _required_ = {
        # FIXME go back to job for job stuff when
        #"job":  {"launcher"}, 
        "workload":  {"launcher"}, 
        #       renaming to fix workload name overload.
        #       task seems to be fine
        "task": {"launcher","resource","main"},
    }
    # TODO 
    _all_ = {
        
    }

    def __init__(self):

        super(JobBuilder, self).__init__()

        self._job_launcher = None
        self._job_configuration = None
        self._script = None
        self._keys = dict()

    @property
    def configured(self):
        return all([
            v is not None for v
            in flatten_list(flatten_dict(self._keys))
        ])

    @property
    def job_configuration(self):
        return self._job_configuration

    @property
    def job_launcher(self):
        '''Job submission CLI command
        that is actually used to submit a job
        to the LRMS.
        '''
        if self._job_launcher is None:
            if self.job_configuration is not None:
                self._configure_launcher()

        return self._job_launcher

    def _configure_launcher(self):

        if self._job_launcher:
            return

        if self.job_configuration:
            # TODO differentiate required vs optional
            #      config keys with 'get' vs hard hash
            print(pformat(self.job_configuration))
            jobopts = self.job_configuration["workload"]
            launcher = jobopts["launcher"]
            launch_args = ' '.join(jobopts["arguments"])
            launch_opts = cli_args_from_dict(jobopts["options"])
            job_launcher = ' '.join(
                [launcher, launch_args, launch_opts])

            job_script = "jobscript.bash"
            self._job_launcher = ' '.join([job_launcher, job_script])

            taskopts = self.job_configuration["task"]
            launcher = taskopts["launcher"]
            launch_args = cli_args_from_dict(taskopts["resource"])
            task_launcher = ' '.join([launcher, launch_args])
            main_exec = taskopts["main"]["executable"]
            main_args = ' '.join(taskopts["main"]["arguments"])
            main_opts = cli_args_from_dict(taskopts["main"]["options"])
            main_line = ' '.join(
                [task_launcher, main_exec, main_args, main_opts])

            script_template = '\n'.join(
                self.job_configuration["job"]["script"])

            self._script = '\n\n'.join(
                [script_template, main_line])

    def load(self, yaml_config, require_on_load=False):

        with open(yaml_config, 'r') as fyml:
            config = yaml.safe_load(fyml)

        print(pformat(config))

        if require_on_load:
            # Should raise exception if not
            # all required fields filled
            self.check_ready_base(config)

        self._job_configuration = config
        self._read_config_keys()

    def check_ready_base(self, config=None):

        if config is None:
            config = self._job_configuration

        for r in self.__class__._required_:

            try:
                assert r in config
                assert all([
                    _r in config[r] for _r
                    in self.__class__._required_[r]
                ])

            except AssertionError as ae:
                print("Missing a required value or subconfig for: '%s'" % r)
                print("from the config file: '%s'" % yaml_config)
                raise ae

    def configure_workload(self, config_dict):
        '''Give a configuration to bind missing parameters.
        If all parameter keys are given values, the `configured`
        attribute will return True and jobs can be launched.
        '''
        assert isinstance(config_dict, dict)

        for k in self._keys:
            self._keys[k] = config_dict[k]

    def _read_config_keys(self):
        '''Keys allow user to hook parameters later
        such as the walltime, number of nodes, etc.
        '''
        flatconfig = flatten_list(flatten_dict(
            self.job_configuration))

        self._keys = {
            k[0]:None for k in
            [get_format_fields(fc) for fc
             in flatconfig if isinstance(fc, str)
            ] if k
        }

    def _write_script(self):
        '''Write a script to submit a job
        '''
        script = self._fill_fields(self._script)

        with open('jobscript.bash', 'w') as fjob:
            fjob.write("#!/bin/bash\n")
            fjob.write(script)

    def _fill_fields(self, template):
        needed_keys = get_format_fields(template)
        kwargs = dict()
        [kwargs.update({k:self._keys[k]}) for k in needed_keys]
        filled = template.format(**kwargs)

        return filled

    def launch_job(self):
        '''Launch a job using the built command
        if the configuration is complete, ie keys
        all have values.
        '''

        if self.configured:
            if not self.job_launcher:
                self._configure_launcher()

            job_launcher = self._fill_fields(self.job_launcher)

            print("Job Launcher")
            print(" -- " + job_launcher)
            if self.__class__._live_:
                self._write_script()

                out, retval = small_proc_watch_block(
                   job_launcher)

                print(out)
                print("")
                print("Any errors during submission? (0 means no, i.e. good thing)")
                print(retval)
                print("")

            else:
                print("Not launching now")
