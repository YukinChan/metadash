#!/usr/bin/env python

import shutil
import glob
import sys
import subprocess

RED, GREEN, NC = '\033[0;31m', '\033[0;32m', '\033[0m'


def error(msg):
    print("{}{}{}".format(RED, msg, NC))


def info(msg):
    print("{}{}{}".format(GREEN, msg, NC))


def do_initialize(dev=False, inst_py_dep=True, inst_node_dep=True, build_assert=False):
    try:
        if not (inst_py_dep or inst_node_dep or build_assert):
            error("*** There is nothing to do! ***")
            sys.exit(1)

        if inst_py_dep:
            info("*** Installing requirements of Metadash ... ***")
            subprocess.run(['pip', 'install', '-r', 'requirements.txt'])
            if dev:
                subprocess.run(['pip', 'install', '-r', 'requirements.dev.txt'])
            info("*** Installing requirements of Metadash Done ***")

            info("*** Installing requirements of Metadash Plugins ... ***")
            for filename in glob.iglob('metadash/plugins/*/requirements.txt'):
                subprocess.run(['pip', 'install', '-r', filename])
            if dev:
                for filename in glob.iglob('metadash/plugins/*/requirements.dev.txt'):
                    subprocess.run(['pip', 'install', '-r', filename])
            info("*** Installing requirements of Metadash Plugins Done ***")

        if inst_node_dep:
            info("*** Install node packages ***")
            if dev:
                subprocess.run(['node', '--max-old-space-size=256', shutil.which('npm'), 'install'])
            else:
                subprocess.run(['node', '--max-old-space-size=256', shutil.which('npm'), 'install', '--production'])
            info("*** Install node packages Done ***")

        if build_assert:
            info("*** Building Asserts ***")
            subprocess.run(['node', '--max-old-space-size=512', 'metadash/build/build.js'])
            info("*** Building Asserts Done ***")

    except Exception as err:
        error("Failed with exception:")
        raise


if __name__ == '__main__':
    try:
        import coloredlogs
        coloredlogs.install(level='INFO')

        # Load Flask
        from metadash import app, db  # noqa

        # Load Manager and Migration
        from flask_migrate import Migrate, MigrateCommand  # noqa
        from flask_script import Manager  # noqa

        migrate = Migrate(app, db)
        manager = Manager(app)
        manager.add_command('db', MigrateCommand)
    except ImportError:
        try:
            _script, cmd, *args = sys.argv
            if cmd == 'initialize':
                dev, only_dep, only_build = False, False, False
                for arg in args:
                    if arg == '--dev':
                        dev = True
                    elif arg == '--only-dependency':
                        only_dep = True
                    elif arg == '--only-build':
                        only_build = True
                    else:
                        error('Unknown arg {}'.format(arg))
                do_initialize(dev,
                              not only_build,
                              not only_build,
                              not only_dep)
                sys.exit(0)
        except Exception:
            pass

        # Will reach here only if manager.py is called,
        # dependency not fully installed, and initialize cmd is not given
        error('Failed with following exception, please '
              'make sure you have ran "manager.py initialize" first!')
        raise

    @manager.command
    @manager.option('-d', '--develop', dest='dev')
    @manager.option('-o', '--only-dependency', dest='only_dep')
    @manager.option('-b', '--only-build', dest='_only_build')
    def initialize(dev=False, only_dep=False, _only_build=False):
        do_initialize(dev,
                      not _only_build,
                      not _only_build,
                      not only_dep)

    @manager.command
    @manager.option('-t', '--testcase', dest='testcase')
    def test_api(testcase=None):
        import unittest
        import os
        from metadash import plugins

        suite = unittest.TestSuite()
        loader = unittest.loader.defaultTestLoader

        if testcase:
            try:
                suite.addTests(loader.loadTestsFromName(testcase))
            except Exception:
                return "Unable to load given test case"
            else:
                pass
        else:
            suite.addTests(loader.loadTestsFromName("metadash.test.api"))

            for file in os.listdir('metadash/test/api'):
                if not file.startswith('_') and not file.startswith('.') and file.endswith('.py'):
                    suite.addTests(loader.loadTestsFromName("metadash.test.api.{}".format(file[:-3])))

            for plugin_name, plugin in plugins.get_all().items():
                try:
                    __import__(plugin['import'] + '.tests')
                except Exception:
                    error("Unable to load test case for plugin {}".format(plugin_name))
                else:
                    suite.addTests(loader.loadTestsFromName(plugin['import'] + '.tests'))

        runner = unittest.TextTestRunner()
        result = runner.run(suite)
        return len(result.errors + result.failures)

    @manager.command
    @manager.option('-n', '--name', dest='name')
    @manager.option('-p', '--password', dest='password')
    @manager.option('-r', '--role', dest='role')
    def create_user(username=None, password=None, role="admin"):
        """
        Create or overlay a user with local authentication
        """
        if username and password:
            from metadash.auth import user_signup, user_setrole
            user_signup(username, password, 'local')
            user_setrole(username, role)
        else:
            raise "Username and password required"

    @manager.command
    def create_database():
        with app.app_context():
            db.create_all()

    manager.run()
