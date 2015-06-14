import os
import traceback
import warnings

import pkg_resources


triggered = False

def trigger():

    global triggered
    if triggered:
        return
    triggered = True

    entry_points = []
    entry_points.extend(pkg_resources.iter_entry_points('sitehooks'))
    entry_points.extend(pkg_resources.iter_entry_points('sitecustomize'))
    entry_points.sort(key=lambda ep: ep.name)

    for entry_point in entry_points:
        try:
            func = entry_point.load()
            func()
        except Exception as e:
            warnings.warn('%s during sitehook %s: %s\n%s' % (
                e.__class__.__name__,
                entry_point,
                e,
                traceback.format_exc(),
            ))


_sitehook_append_path = '''
import sys
sys.path.append(%r)
'''.strip()

_sitehook_template = '''
try:
    import {module}
    {module}.{func}({argspec})
except Exception as e:
    warnings.warn('%s during sitehook.trigger(): %s' % (e.__class__.__name__, e))
'''.strip().replace('   ', '\t')


def install(site_packages, module, func, prefix='zzz_',
    args=None, kwargs=None, append_path=True, verbose=False, dry_run=False
):

    hook_path = os.path.join(site_packages, '%s%s_%s.pth' % (prefix, module, func))
    if verbose:
        print 'installing:', hook_path

    argspec = []
    if args:
        argspec.extend(map(repr, args))
    if kwargs:
        argspec.extend('%s=%r' % (k, v) for k, v in sorted(kwargs.iteritems()))

    hook_source = [_sitehook_template.format(
        module=module,
        func=func,
        argspec=', '.join(argspec)
    )]
    if append_path:
        import_path = os.path.abspath(os.path.join(__file__, '..', '..'))
        if verbose:
            print 'will import sitehooks from:', import_path
        hook_source.insert(0, _sitehook_append_path % import_path)

    if dry_run:
        return
    with open(hook_path, 'w') as fh:
        fh.write('import warnings; exec %r\n' % '\n'.join(hook_source))


def uninstall(site_packages, module, func=None, prefix=None,
    verbose=False, dry_run=False
):
    pattern = (prefix or '*') + module + ('_' + func if func else '*') + '.pth'
    for hook_path in glob.glob(os.path.join(site_packages, pattern)):
        if verbose:
            print 'uninstalling:', hook_path
        if dry_run:
            continue
        os.unlink(hook_path)


